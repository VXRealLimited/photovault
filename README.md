# PhotoVault 🔒📷

> **Hide your secrets in your own photos.**

**PhotoVault** is a simple, easy-to-use tool that lets you hide private notes, passwords, or messages inside your favorite photos.

Instead of remembering complex passwords, **PhotoVault uses the order of your chosen photos to unlock your secrets**. Simply pick a set of photos in an order you can easily remember (like photos from a trip or a favorite photo album), hide your secret, and reload those same photos in the same order whenever you need to read it again.

---

## 🌟 Why Use PhotoVault?

- **No Passwords to Remember:** Your photo choices and their order act as your personal lock and key.
- **Invisible to Others:** Your photos look completely normal to anyone else viewing them. The hidden message is completely invisible.
- **Simple Desktop App:** Built with an easy-to-use visual interface—no technical skills or coding required.
- **Fast & Lightweight:** Protects and unlocks your secrets instantly.
- **Rotation Proof:** Works smoothly even if your photos get rotated on different devices.

---

## ⚠️ Important Note on Sharing Photos

If you plan to send your PhotoVault photos to someone via apps like **WhatsApp**, **Telegram**, or **Discord**:

> **Always send them as a "Document" or "File" (uncompressed).**

Sending them as regular standard photos causes chat apps to shrink and compress the image, which erases the hidden message data inside.

---

## 🚀 Getting Started

### 1. Installation

Download or clone the repository, then install the required tools:

```bash
pip install -r requirements.txt
```

---

## 🕹️ How to Use

### 1. Launch the App (GUI)

Run the following command to open the visual app interface:

```bash
python main.py
```

- **Hide Secret:** Type your private message, add your chosen photos, arrange them in your preferred order, and click **Embed & Save**.
- **Reveal Secret:** Load your saved photos in the exact same order and click **Reveal Secret** to display your message.

---

### 2. Try the Quick Demo

Want to see how it works first? Run the built-in test demo:

```bash
python main.py --demo
```

This test automatically loads test images, hides a sample secret, extracts it, and shows what happens if someone tries to load the photos in the wrong order.

---

## 💻 Developer API Example

If you want to use PhotoVault inside your own Python projects:

```python
from photovault import hide_secret, reveal_secret

# Select your images in order
my_photos = ["photo1.jpg", "photo2.jpg", "photo3.jpg", "photo4.jpg"]
saved_vault_photos = ["vault1.png", "vault2.png", "vault3.png", "vault4.png"]

# 1. Hide your secret
hide_secret("My top secret note", my_photos, saved_vault_photos)

# 2. Read it back
secret = reveal_secret(saved_vault_photos)
print("My Secret:", secret)
```

---
