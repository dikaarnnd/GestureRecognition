import os
from customtkinter import *
from tkinter import filedialog
from PIL import Image

# Direktori untuk menyimpan foto
GALLERY_DIR = "gallery_photos"
os.makedirs(GALLERY_DIR, exist_ok=True)

# Mengatur mode dan tema
set_appearance_mode("dark")  # Mode tampilan (Light/Dark/System)
set_default_color_theme("blue")  # Tema warna (blue/dark/light)

def upload_photo():
    """Mengunggah foto ke gallery."""
    file_path = filedialog.askopenfilename(
        title="Pilih Foto",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
    )
    if file_path:
        try:
            file_name = os.path.basename(file_path)
            save_path = os.path.join(GALLERY_DIR, file_name)
            if os.path.exists(save_path):
                CTkComboBox(title="Error", message="Foto dengan nama ini sudah ada di gallery.", icon="error")
            else:
                with open(file_path, "rb") as source:
                    with open(save_path, "wb") as target:
                        target.write(source.read())
                CTkComboBox(title="Sukses", message="Foto berhasil disimpan.", icon="info")
                display_gallery()
        except Exception as e:
            CTkComboBox(title="Error", message=f"Gagal menyimpan foto: {str(e)}", icon="error")

def display_gallery():
    """Menampilkan foto di gallery."""
    for widget in gallery_frame.winfo_children():
        widget.destroy()

    photos = os.listdir(GALLERY_DIR)
    if not photos:
        CTkLabel(gallery_frame, text="Gallery Kosong", font=("Arial", 12)).pack(pady=10)
        return

    for photo in photos:
        try:
            photo_path = os.path.join(GALLERY_DIR, photo)
            img = Image.open(photo_path)
            img.thumbnail((150, 150))  # Menyesuaikan ukuran thumbnail
            ctk_image = CTkImage(light_image=img, dark_image=img, size=(150, 150))  # Gunakan CTkImage
            
            frame = CTkFrame(gallery_frame, corner_radius=5)
            frame.pack(side="left", padx=5, pady=5)
            
            label = CTkLabel(frame, image=ctk_image, text="")  # Gunakan CTkImage
            label.image = ctk_image
            label.pack()

            CTkLabel(frame, text=photo, font=("Arial", 8)).pack()
        except Exception as e:
            print(f"Gagal memuat foto: {photo} - {e}")

# Setup GUI
root = CTk()
root.title("Gallery App")
root.geometry("600x400")

# Header
header_frame = CTkFrame(root, corner_radius=0, bg_color="#a3b7ca")  # Menambahkan bg_color
header_frame.pack(fill="x")

CTkLabel(header_frame, text="Gallery App", font=("Arial", 16, "bold")).pack(side="left", padx=10)

upload_button = CTkButton(header_frame, text="Upload Foto", command=upload_photo, hover_color="#809bce")
upload_button.pack(side="right", padx=10)

# Frame untuk gallery
gallery_frame = CTkFrame(root)
gallery_frame.pack(fill="both", expand=True)

# Scrollable gallery
canvas = CTkCanvas(gallery_frame, highlightthickness=0)
scrollbar = CTkScrollbar(gallery_frame, orientation="vertical", command=canvas.yview)
gallery_content = CTkFrame(canvas)

gallery_content.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=gallery_content, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

gallery_frame = gallery_content

# Load awal
display_gallery()

root.mainloop()
