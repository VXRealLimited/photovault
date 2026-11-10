import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List

from .core import hide_secret, reveal_secret, PhotoVaultError, CompressionError


class PhotoVaultGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PhotoVault - Hide Secrets in Image Sequences")
        self.root.geometry("640x540")
        self.root.resizable(False, False)

        # Internal list of full file paths: [(filename_display, full_path)]
        self.hide_files: List[str] = []
        self.reveal_files: List[str] = []

        # Tab Control
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_hide = ttk.Frame(self.notebook)
        self.tab_reveal = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_hide, text=" Hide Secret ")
        self.notebook.add(self.tab_reveal, text=" Reveal Secret ")

        self._build_hide_tab()
        self._build_reveal_tab()

    def _build_hide_tab(self):
        lbl_secret = ttk.Label(self.tab_hide, text="Secret Message / Key:")
        lbl_secret.pack(anchor="w", padx=15, pady=(10, 2))

        self.txt_secret = tk.Text(self.tab_hide, height=4, width=70)
        self.txt_secret.pack(padx=15, pady=2)

        lbl_imgs = ttk.Label(
            self.tab_hide, text="Cover Images (Ordered top-to-bottom):"
        )
        lbl_imgs.pack(anchor="w", padx=15, pady=(10, 2))

        frame_list = ttk.Frame(self.tab_hide)
        frame_list.pack(padx=15, pady=2, fill="x")

        self.lst_hide_imgs = tk.Listbox(frame_list, height=6, selectmode=tk.SINGLE)
        self.lst_hide_imgs.pack(side="left", fill="both", expand=True)

        frame_btn = ttk.Frame(frame_list)
        frame_btn.pack(side="right", fill="y", padx=(5, 0))

        ttk.Button(frame_btn, text="Add Images...", command=self._add_hide_images).pack(
            fill="x", pady=2
        )
        ttk.Button(frame_btn, text="Move Up", command=self._move_hide_up).pack(
            fill="x", pady=2
        )
        ttk.Button(frame_btn, text="Move Down", command=self._move_hide_down).pack(
            fill="x", pady=2
        )
        ttk.Button(frame_btn, text="Clear", command=self._clear_hide_images).pack(
            fill="x", pady=2
        )

        notice_lbl = ttk.Label(
            self.tab_hide,
            text="⚠️ IMPORTANT: Always send output photos as UNCOMPRESSED DOCUMENTS on WhatsApp/Telegram.",
            foreground="darkorange",
            wraplength=580,
        )
        notice_lbl.pack(padx=15, pady=10)

        btn_hide = ttk.Button(
            self.tab_hide,
            text="🔒 Embed & Save Vault Images",
            command=self._process_hide,
        )
        btn_hide.pack(padx=15, pady=10, fill="x")

    def _build_reveal_tab(self):
        lbl_imgs = ttk.Label(
            self.tab_reveal, text="Stego Images in EXACT Sequence Order:"
        )
        lbl_imgs.pack(anchor="w", padx=15, pady=(10, 2))

        frame_list = ttk.Frame(self.tab_reveal)
        frame_list.pack(padx=15, pady=2, fill="x")

        self.lst_reveal_imgs = tk.Listbox(frame_list, height=7, selectmode=tk.SINGLE)
        self.lst_reveal_imgs.pack(side="left", fill="both", expand=True)

        frame_btn = ttk.Frame(frame_list)
        frame_btn.pack(side="right", fill="y", padx=(5, 0))

        ttk.Button(
            frame_btn, text="Add Images...", command=self._add_reveal_images
        ).pack(fill="x", pady=2)
        ttk.Button(frame_btn, text="Move Up", command=self._move_reveal_up).pack(
            fill="x", pady=2
        )
        ttk.Button(frame_btn, text="Move Down", command=self._move_reveal_down).pack(
            fill="x", pady=2
        )
        ttk.Button(frame_btn, text="Clear", command=self._clear_reveal_images).pack(
            fill="x", pady=2
        )

        btn_reveal = ttk.Button(
            self.tab_reveal, text="🔓 Reveal Secret", command=self._process_reveal
        )
        btn_reveal.pack(padx=15, pady=10, fill="x")

        lbl_result = ttk.Label(self.tab_reveal, text="Extracted Secret:")
        lbl_result.pack(anchor="w", padx=15, pady=(5, 2))

        self.txt_reveal_result = tk.Text(
            self.tab_reveal, height=4, width=70, state="disabled"
        )
        self.txt_reveal_result.pack(padx=15, pady=2)

    # --- Helper to refresh Listbox UI from path list ---
    def _refresh_hide_listbox(self):
        self.lst_hide_imgs.delete(0, tk.END)
        for f in self.hide_files:
            self.lst_hide_imgs.insert(tk.END, os.path.basename(f))

    def _refresh_reveal_listbox(self):
        self.lst_reveal_imgs.delete(0, tk.END)
        for f in self.reveal_files:
            self.lst_reveal_imgs.insert(tk.END, os.path.basename(f))

    # --- Hide Tab Handlers ---
    def _add_hide_images(self):
        files = filedialog.askopenfilenames(
            title="Select Cover Images",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")],
        )
        for f in files:
            if f not in self.hide_files:
                self.hide_files.append(f)
        self._refresh_hide_listbox()

    def _move_hide_up(self):
        idx = self.lst_hide_imgs.curselection()
        if idx and idx[0] > 0:
            i = idx[0]
            self.hide_files[i], self.hide_files[i - 1] = (
                self.hide_files[i - 1],
                self.hide_files[i],
            )
            self._refresh_hide_listbox()
            self.lst_hide_imgs.selection_set(i - 1)

    def _move_hide_down(self):
        idx = self.lst_hide_imgs.curselection()
        if idx and idx[0] < len(self.hide_files) - 1:
            i = idx[0]
            self.hide_files[i], self.hide_files[i + 1] = (
                self.hide_files[i + 1],
                self.hide_files[i],
            )
            self._refresh_hide_listbox()
            self.lst_hide_imgs.selection_set(i + 1)

    def _clear_hide_images(self):
        self.hide_files.clear()
        self._refresh_hide_listbox()

    def _process_hide(self):
        secret = self.txt_secret.get("1.0", tk.END).strip()
        if not secret:
            messagebox.showerror("Error", "Please enter a secret message.")
            return
        if len(self.hide_files) < 2:
            messagebox.showerror("Error", "Please select at least 2 cover images.")
            return

        save_dir = filedialog.askdirectory(title="Select Folder to Save Vault PNGs")
        if not save_dir:
            return

        outputs = [
            os.path.join(save_dir, f"photovault_{i+1}.png")
            for i in range(len(self.hide_files))
        ]

        try:
            hide_secret(secret, self.hide_files, outputs)
            messagebox.showinfo(
                "Success",
                f"Successfully hid secret across {len(outputs)} images!\nSaved to:\n{save_dir}",
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- Reveal Tab Handlers ---
    def _add_reveal_images(self):
        files = filedialog.askopenfilenames(
            title="Select Vault Images",
            filetypes=[("PNG Images", "*.png"), ("All Files", "*.*")],
        )
        for f in files:
            if f not in self.reveal_files:
                self.reveal_files.append(f)
        self._refresh_reveal_listbox()

    def _move_reveal_up(self):
        idx = self.lst_reveal_imgs.curselection()
        if idx and idx[0] > 0:
            i = idx[0]
            self.reveal_files[i], self.reveal_files[i - 1] = (
                self.reveal_files[i - 1],
                self.reveal_files[i],
            )
            self._refresh_reveal_listbox()
            self.lst_reveal_imgs.selection_set(i - 1)

    def _move_reveal_down(self):
        idx = self.lst_reveal_imgs.curselection()
        if idx and idx[0] < len(self.reveal_files) - 1:
            i = idx[0]
            self.reveal_files[i], self.reveal_files[i + 1] = (
                self.reveal_files[i + 1],
                self.reveal_files[i],
            )
            self._refresh_reveal_listbox()
            self.lst_reveal_imgs.selection_set(i + 1)

    def _clear_reveal_images(self):
        self.reveal_files.clear()
        self._refresh_reveal_listbox()

    def _process_reveal(self):
        if not self.reveal_files:
            messagebox.showerror("Error", "Please select vault images to reveal.")
            return

        try:
            secret = reveal_secret(self.reveal_files)
            self.txt_reveal_result.config(state="normal")
            self.txt_reveal_result.delete("1.0", tk.END)
            self.txt_reveal_result.insert(tk.END, secret)
            self.txt_reveal_result.config(state="disabled")
            messagebox.showinfo("Success", "Secret extracted successfully!")
        except CompressionError as e:
            messagebox.showerror("Compression / Corruption Error", str(e))
        except Exception as e:
            messagebox.showerror("Extraction Error", str(e))


def launch_gui():
    root = tk.Tk()
    app = PhotoVaultGUI(root)
    root.mainloop()
