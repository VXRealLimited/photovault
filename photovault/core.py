import os
import struct
import zlib
import hashlib
from typing import List
from PIL import Image, ImageOps
import numpy as np

MAGIC_HEADER = b"PV10"
SAMPLE_SIZE = 4096  # 4KB head + 4KB tail sample per image for instant key derivation

class PhotoVaultError(Exception):
    """Base exception for PhotoVault operations."""
    pass

class CompressionError(PhotoVaultError):
    """Raised when image compression or corruption destroys payload."""
    pass

class CapacityError(PhotoVaultError):
    """Raised when cover images lack sufficient pixel capacity."""
    pass


def _derive_fast_sequence_key(image_paths: List[str]) -> bytes:
    """
    Derives a 256-bit AES master key instantly by sampling boundary bits 
    of each image in sequence order, masking out the LSB so the key remains 
    identical before and after payload embedding.
    """
    hasher = hashlib.sha256()
    for path in image_paths:
        try:
            raw_img = Image.open(path)
            img = ImageOps.exif_transpose(raw_img).convert("RGB")
            
            # Feed image dimensions
            hasher.update(struct.pack(">II", img.width, img.height))
            
            # Convert sample bytes to numpy array to zero out LSB (mask 0xFE)
            raw_bytes = img.tobytes()
            
            # Sample head and tail
            head_sample = np.frombuffer(raw_bytes[:SAMPLE_SIZE], dtype=np.uint8) & np.uint8(0xFE)
            tail_sample = np.frombuffer(raw_bytes[-SAMPLE_SIZE:], dtype=np.uint8) & np.uint8(0xFE)
            
            hasher.update(head_sample.tobytes())
            hasher.update(tail_sample.tobytes())
        except Exception as e:
            raise PhotoVaultError(f"Failed to read image '{path}' for key generation: {e}")
            
    return hasher.digest()


def _fast_embed_bits(image_path: str, payload_bytes: bytes, output_path: str):
    """Vectorized LSB embedding using NumPy arrays."""
    raw_img = Image.open(image_path)
    img = ImageOps.exif_transpose(raw_img).convert("RGB")
    arr = np.array(img, dtype=np.uint8)
    
    # 32-bit length header + payload
    payload_bits = np.unpackbits(np.frombuffer(payload_bytes, dtype=np.uint8))
    len_bits = np.unpackbits(np.array([len(payload_bits)], dtype=np.uint32).view(np.uint8)[::-1])
    full_bits = np.concatenate([len_bits, payload_bits]).astype(np.uint8)
    
    flat_arr = arr.ravel()
    if len(full_bits) > len(flat_arr):
        raise CapacityError(f"Image '{image_path}' is too small to store payload slice.")
        
    # FIX: Use np.uint8(0xFE) instead of ~1 to prevent signed integer overflow (-2)
    mask = np.uint8(0xFE) # 0b11111110
    flat_arr[:len(full_bits)] = (flat_arr[:len(full_bits)] & mask) | full_bits
    
    output_img = Image.fromarray(arr.reshape(img.height, img.width, 3))
    output_img.save(output_path, format="PNG")


def _fast_extract_bits_from_orientation(img: Image.Image) -> bytes:
    """Vectorized bit extraction from NumPy array."""
    arr = np.array(img, dtype=np.uint8).ravel()
    if len(arr) < 32:
        return None
        
    # Read 32-bit payload length
    len_bits = arr[:32] & 1
    payload_bit_len = int("".join(len_bits.astype(str)), 2)
    
    if payload_bit_len <= 0 or payload_bit_len > (len(arr) - 32):
        return None
        
    payload_bits = arr[32:32 + payload_bit_len] & 1
    
    # Pack bits back into bytes
    byte_array = np.packbits(payload_bits)
    return byte_array.tobytes()


def _extract_bits_from_image(image_path: str) -> bytes:
    """Extract embedded container, testing 4 rotation orientations instantly."""
    try:
        raw_img = Image.open(image_path)
        img = ImageOps.exif_transpose(raw_img).convert("RGB")
    except Exception as e:
        raise PhotoVaultError(f"Failed to open image '{image_path}': {e}")
        
    orientations = [
        img,
        img.transpose(Image.ROTATE_90),
        img.transpose(Image.ROTATE_180),
        img.transpose(Image.ROTATE_270),
    ]

    for oriented_img in orientations:
        payload = _fast_extract_bits_from_orientation(oriented_img)
        if payload is not None:
            return payload

    raise CompressionError(f"No valid payload container found in '{image_path}'.")


def hide_secret(secret_text: str, cover_images: List[str], output_images: List[str]) -> List[str]:
    """Hides secret using high-speed sampling and vectorized LSB embedding."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    if len(cover_images) < 2 or len(cover_images) != len(output_images):
        raise PhotoVaultError("Image count mismatch or insufficient cover images.")
        
    # Instant key derivation from boundary pixels
    master_key = _derive_fast_sequence_key(cover_images)
    aesgcm = AESGCM(master_key)
    
    raw_payload = secret_text.encode('utf-8')
    num_parts = len(cover_images)
    
    chunk_size = (len(raw_payload) + num_parts - 1) // num_parts
    chunks = [raw_payload[i:i + chunk_size] for i in range(0, len(raw_payload), chunk_size)]
    while len(chunks) < num_parts:
        chunks.append(b"")
        
    saved_paths = []
    for idx, (cover_path, chunk) in enumerate(zip(cover_images, chunks)):
        crc = zlib.crc32(chunk)
        inner_plaintext = MAGIC_HEADER + bytes([num_parts, idx]) + struct.pack(">I", crc) + chunk
        
        nonce = hashlib.md5(f"nonce_{idx}".encode()).digest()[:12]
        encrypted_container = aesgcm.encrypt(nonce, inner_plaintext, None)
        
        _fast_embed_bits(cover_path, encrypted_container, output_images[idx])
        saved_paths.append(output_images[idx])
        
    return saved_paths


def reveal_secret(ordered_stego_images: List[str]) -> str:
    """Reveals secret using high-speed sampling and vectorized LSB extraction."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    if not ordered_stego_images:
        raise PhotoVaultError("No stego images provided.")
        
    master_key = _derive_fast_sequence_key(ordered_stego_images)
    aesgcm = AESGCM(master_key)
    
    extracted_chunks = []
    expected_total = len(ordered_stego_images)
    
    for idx, img_path in enumerate(ordered_stego_images):
        container = _extract_bits_from_image(img_path)
        nonce = hashlib.md5(f"nonce_{idx}".encode()).digest()[:12]
        
        try:
            inner_plaintext = aesgcm.decrypt(nonce, container, None)
        except Exception:
            raise PhotoVaultError(
                "Failed to decrypt vault. The image sequence or selection is INCORRECT, "
                "or the images have been corrupted/compressed."
            )
            
        if len(inner_plaintext) < 10 or inner_plaintext[:4] != MAGIC_HEADER:
            raise CompressionError("Header validation failed.")
            
        total_parts = inner_plaintext[4]
        part_idx = inner_plaintext[5]
        expected_crc = struct.unpack(">I", inner_plaintext[6:10])[0]
        chunk_data = inner_plaintext[10:]
        
        if total_parts != expected_total or part_idx != idx:
            raise PhotoVaultError("Image sequence or selection mismatch.")
            
        if zlib.crc32(chunk_data) != expected_crc:
            raise CompressionError(f"Checksum verification failed for part {idx + 1}.")
            
        extracted_chunks.append(chunk_data)
        
    return b"".join(extracted_chunks).decode('utf-8')