import customtkinter
from tkinter import filedialog
from PIL import Image, ImageTk
import os

folder = "gallery_photos"

# Fungsi untuk memuat foto dari folder
def load_photos():
    if not os.path.exists(folder):  # Periksa apakah folder ada
        os.makedirs(folder)  # Jika tidak, buat folder

    for widget in appFrame.winfo_children():  # Hapus widget sebelumnya
        widget.destroy()

    # Dapatkan lebar aplikasi saat ini
    frame_width = appFrame.winfo_width()
    # print(frame_width)

    # Tentukan jumlah kolom berdasarkan ukuran lebar frame
    if frame_width >= 1200:
        columns = 8
    elif frame_width >= 600:
        columns = 4
    elif frame_width >= 400:
        columns = 3
    elif frame_width >= 200:
        columns = 3
    else:
        columns = 2

    padding = 10  # Padding antar gambar
    row = 0
    col = 0

    # Loop untuk membaca file gambar di folder
    for filename in os.listdir(folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
            filepath = os.path.join(folder, filename)
            try:
                # Buka gambar
                img = Image.open(filepath)

                # Tentukan ukuran gambar (150x150px)
                photo = customtkinter.CTkImage(img, size=(150, 150))

                # Label gambar
                img_label = customtkinter.CTkLabel(appFrame, image=photo, text="")
                img_label.image = photo  # Simpan referensi gambar agar tidak dihapus
                img_label.grid(row=row, column=col, padx=padding, pady=padding)

                # Perbarui posisi kolom dan baris
                col += 1
                if col >= columns:
                    col = 0
                    row += 1
            except Exception as e:
                print(f"Error loading {filename}: {e}")

# Fungsi untuk memonitor perubahan ukuran frame
def monitor_frame_size():
    global last_frame_width

    # Periksa lebar frame saat ini
    current_width = appFrame.winfo_width()

    # Jika lebar frame berubah, panggil load_photos()
    if current_width != last_frame_width:
        last_frame_width = current_width
        load_photos()

    # Jalankan fungsi ini lagi setelah 100ms
    app.after(100, monitor_frame_size)

# Fungsi untuk mengunggah gambar
def upload_photo():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")]
    )
    if file_path:
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(folder, file_name)
        if not os.path.exists(dest_path):
            Image.open(file_path).save(dest_path)
        load_photos()

# Inisialisasi aplikasi
app = customtkinter.CTk()
app.geometry("700x600")
app.title("Gallery")

# Header
header = customtkinter.CTkFrame(
    app, 
    fg_color="lightblue",
    width=700,
    height=40
)
# Kolom header
header.grid_columnconfigure(0, weight=1)  # Kolom teks
header.grid_columnconfigure(1, weight=0)  # Kolom tombol upload
header.grid_columnconfigure(2, weight=0)  # Kolom tombol select
header.pack(pady=5, fill="x")  # Atur header agar mengisi lebar penuh aplikasi

# Header untuk teks
header_text = customtkinter.CTkLabel(
    master=header,
    text="My Gallery",
    font=("Arial", 16, "bold"),
    text_color="black",
    anchor="w"  # Posisi teks di kiri
)
header_text.grid(row=0, column=0, padx=10, sticky="w")  # sticky="w" teks tetap di kiri

# Upload Button di Header
uploadBtn = customtkinter.CTkButton(
    master=header,
    text="Upload",
    hover_color="#3b47d1",
    width=100,
    height=30,
    command=upload_photo
)
uploadBtn.grid(row=0, column=1, padx=10, pady=5, sticky="e")  # sticky="e" agar tombol tetap di kanan

# Select Button di Header
selectdBtn = customtkinter.CTkButton(
    master=header,
    text="Select",
    hover_color="#3b47d1",
    width=100,
    height=30
    # command=select_photo
)
selectdBtn.grid(row=0, column=2, padx=10, pady=5, sticky="e")  # sticky="e" agar tombol tetap di kanan

# Scrollable Frame
appFrame = customtkinter.CTkScrollableFrame(
    app,
    width=700,
    height=800
)
appFrame.pack(pady=10, fill="both", expand=True)

# Inisialisasi variabel untuk memantau ukuran frame
last_frame_width = appFrame.winfo_width()

# Panggil fungsi load_photos() untuk pertama kali
load_photos()

# Memonitor perubahan ukuran frame
monitor_frame_size()

# Menjalankan aplikasi
app.mainloop()
