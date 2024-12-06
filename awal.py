import os
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Direktori untuk menyimpan foto
GALLERY_DIR = "gallery_photos"
os.makedirs(GALLERY_DIR, exist_ok=True)

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
                messagebox.showerror("Error", "Foto dengan nama ini sudah ada di gallery.")
            else:
                with open(file_path, "rb") as source:
                    with open(save_path, "wb") as target:
                        target.write(source.read())
                messagebox.showinfo("Sukses", "Foto berhasil disimpan.")
                display_gallery()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan foto: {str(e)}")

def display_gallery():
    """Menampilkan foto di gallery."""
    for widget in gallery_frame.winfo_children():
        widget.destroy()

    photos = os.listdir(GALLERY_DIR)
    if not photos:
        Label(gallery_frame, text="Gallery Kosong", font=("Arial", 12), pady=10).pack()
        return

    for photo in photos:
        try:
            photo_path = os.path.join(GALLERY_DIR, photo)
            img = Image.open(photo_path)
            img.thumbnail((150, 150))
            photo_img = ImageTk.PhotoImage(img)
            
            frame = Frame(gallery_frame, padx=5, pady=5)
            frame.pack(side=LEFT)
            
            label = Label(frame, image=photo_img)
            label.image = photo_img
            label.pack()

            Label(frame, text=photo, font=("Arial", 8)).pack()
        except Exception as e:
            print(f"Gagal memuat foto: {photo} - {e}")

def delete_gallery():
    """Menghapus semua foto di gallery."""
    if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus semua foto?"):
        for photo in os.listdir(GALLERY_DIR):
            os.remove(os.path.join(GALLERY_DIR, photo))
        display_gallery()
        messagebox.showinfo("Sukses", "Semua foto telah dihapus.")

# Setup GUI
root = Tk()
root.title("Gallery App")
root.geometry("600x400")

# Frame untuk tombol
button_frame = Frame(root)
button_frame.pack(pady=10)

Button(button_frame, text="Upload Foto", command=upload_photo).pack(side=LEFT, padx=5)
Button(button_frame, text="Hapus Semua Foto", command=delete_gallery).pack(side=LEFT, padx=5)

# Frame untuk gallery
gallery_frame = Frame(root)
gallery_frame.pack(fill=BOTH, expand=True)

# Scrollable gallery
canvas = Canvas(gallery_frame)
scrollbar = Scrollbar(gallery_frame, orient=VERTICAL, command=canvas.yview)
gallery_content = Frame(canvas)

gallery_content.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=gallery_content, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.pack(side=RIGHT, fill=Y)

gallery_frame = gallery_content

# Load awal
display_gallery()

root.mainloop()
