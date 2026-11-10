import os
import sys
from photovault.gui import launch_gui
from photovault.core import hide_secret, reveal_secret, PhotoVaultError


def run_demo():
    print("=== PhotoVault 4-Image Sequence Steganography Demo ===")

    # 1. Define paths to your test cover images
    test_dir = "test_imgs"
    cover_images = [
        os.path.join(test_dir, "cover1.jpg"),
        os.path.join(test_dir, "cover2.jpg"),
        os.path.join(test_dir, "cover3.jpg"),
        os.path.join(test_dir, "cover4.jpg"),
    ]

    # Destination output paths (always save stego images as lossless PNG)
    output_dir = "output_vault"
    os.makedirs(output_dir, exist_ok=True)

    stego_images = [
        os.path.join(output_dir, "vault_1.png"),
        os.path.join(output_dir, "vault_2.png"),
        os.path.join(output_dir, "vault_3.png"),
        os.path.join(output_dir, "vault_4.png"),
    ]

    # Verify input images exist
    for cover in cover_images:
        if not os.path.exists(cover):
            print(f"Error: Test cover image '{cover}' not found.")
            return

    secret_message = "CONFIDENTIAL_API_KEY_987654321_XYZ"
    print(f"\n1. Original Secret Message: '{secret_message}'")

    # 2. Embed secret across the 4 cover images
    print("\n2. Embedding secret across test images...")
    try:
        hide_secret(secret_message, cover_images, stego_images)
        print("   [SUCCESS] Embedded into:")
        for path in stego_images:
            print(f"   - {path}")
    except Exception as e:
        print(f"   [ERROR] Failed to hide secret: {e}")
        return

    # 3. Test correct sequence extraction
    print("\n3. Attempting reconstruction with CORRECT image sequence...")
    try:
        revealed = reveal_secret(stego_images)
        print(f"   [SUCCESS] Revealed Secret: '{revealed}'")
    except Exception as e:
        print(f"   [ERROR] Failed to extract secret: {e}")

    # 4. Test wrong sequence extraction (Order-dependence check)
    print(
        "\n4. Attempting reconstruction with WRONG image sequence (Order: 3 -> 1 -> 4 -> 2)..."
    )
    wrong_order = [stego_images[2], stego_images[0], stego_images[3], stego_images[1]]
    try:
        revealed = reveal_secret(wrong_order)
        print(f"   Revealed Secret: '{revealed}'")
    except PhotoVaultError as e:
        print(
            f"   [SUCCESS - Sequence Blocked]: Decryption failed as expected!\n   Reason: {e}"
        )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()
    else:
        # Launch GUI by default if no flags passed
        launch_gui()
