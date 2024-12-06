from customtkinter import *
from tkinter import filedialog, Canvas, Scrollbar
from PIL import Image, ImageTk
import os

# Inisialisasi aplikasi
app = CTk()
app.geometry("700x700")
app.title("Gallery")

# Direktori untuk menyimpan foto
GALLERY_DIR = "gallery_photos"
os.makedirs(GALLERY_DIR, exist_ok=True)

# Fungsi untuk mengunggah gambar
def upload_photo():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")]
    )
    if file_path:
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(GALLERY_DIR, file_name)
        if not os.path.exists(dest_path):
            Image.open(file_path).save(dest_path)
        load_images()

# Fungsi untuk menghapus gambar
def delete_photo(image_path):
    if os.path.exists(image_path):
        os.remove(image_path)
        load_images()

# Fungsi untuk memuat dan menampilkan gambar
def load_images():
    for widget in canvas_frame.winfo_children():
        widget.destroy()

    images = [
        os.path.join(GALLERY_DIR, img) for img in os.listdir(GALLERY_DIR)
        if img.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))
    ]

    row, col = 0, 0
    for image_path in images:
        try:
            img = Image.open(image_path)
            img.thumbnail((150, 150))
            photo = ImageTk.PhotoImage(img)

            frame = CTkFrame(master=canvas_frame, corner_radius=10)
            frame.grid(row=row, column=col, padx=10, pady=10)

            img_label = CTkLabel(master=frame, image=photo, text="")
            img_label.image = photo  # Simpan referensi agar tidak dihapus oleh garbage collector
            img_label.pack()

            delete_btn = CTkButton(
                master=frame,
                text="Delete",
                fg_color="#e74c3c",
                hover_color="#c0392b",
                command=lambda path=image_path: delete_photo(path)
            )
            delete_btn.pack(pady=5)

            col += 1
            if col >= 4:  # 4 gambar per baris
                col = 0
                row += 1
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")

    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Header frame
header = CTkFrame(master=app, height=50, corner_radius=0, fg_color="#2c3e50")
header.pack(fill="x", side="top")

header_label = CTkLabel(
    master=header,
    text="MyGallery",
    text_color="white",
    font=("Arial", 18)
)
header_label.pack(side="left", padx=20, pady=10)

uploadBtn = CTkButton(
    master=header,
    text="Upload",
    corner_radius=32,
    fg_color="#5091bf",
    hover_color="#3b47d1",
    width=100,
    command=upload_photo
)
uploadBtn.pack(side="right", padx=20, pady=10)

# Canvas untuk scroll
canvas = Canvas(app, bg="#f0f0f0")
canvas.pack(side=LEFT, fill=BOTH, expand=True)

scrollbar = Scrollbar(app, orient=VERTICAL, command=canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)

canvas.configure(yscrollcommand=scrollbar.set)

canvas_frame = CTkFrame(canvas)
canvas.create_window((0, 0), window=canvas_frame, anchor="nw")

# Load gambar saat aplikasi dijalankan
load_images()

# Menjalankan aplikasi
app.mainloop()
