import customtkinter
from tkinter import filedialog
from PIL import Image
import os
import mysql.connector

checkboxes = {}
delete_mode = False
is_fullscreen_preview = False  # Status preview fullscreen aktif/tidak

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gallery_app"
    )

def open_fullscreen_preview(filepath):
    global is_fullscreen_preview
    try:
        image = Image.open(filepath)

        frame_width = app.winfo_width()
        frame_height = app.winfo_height() - 50  # kurangi header

        image.thumbnail((frame_width, frame_height), Image.Resampling.LANCZOS)
        photo = customtkinter.CTkImage(light_image=image, size=image.size)

        previewImageLabel.configure(image=photo, text="")
        previewImageLabel.image = photo

        appFrame.pack_forget()
        previewFrame.pack(fill="both", expand=True, pady=0)

        is_fullscreen_preview = True
    except Exception as e:
        print(f"Error previewing image: {e}")

def close_fullscreen_preview():
    global is_fullscreen_preview
    previewFrame.pack_forget()
    appFrame.pack(pady=10, fill="both", expand=True)
    is_fullscreen_preview = False

def handle_escape(event):
    if is_fullscreen_preview:
        close_fullscreen_preview()

def load_photos():
    for widget in appFrame.winfo_children():
        widget.destroy()

    frame_width = appFrame.winfo_width()
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

    padding = 10
    row = 0
    col = 0
    checkboxes.clear()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, image_path FROM images")
    image_entries = cursor.fetchall()
    conn.close()

    for img_id, filepath in image_entries:
        if os.path.exists(filepath):
            try:
                img = Image.open(filepath)
                photo = customtkinter.CTkImage(img, size=(150, 150))

                photo_frame = customtkinter.CTkFrame(appFrame, fg_color="transparent")
                photo_frame.grid(row=row, column=col, padx=padding, pady=padding)

                img_label = customtkinter.CTkLabel(photo_frame, image=photo, text="")
                img_label.image = photo
                img_label.pack()
                img_label.bind("<Button-1>", lambda e, path=filepath: open_fullscreen_preview(path))

                var = customtkinter.BooleanVar()
                checkbox = customtkinter.CTkCheckBox(photo_frame, text="", variable=var)
                checkbox.pack(pady=5)
                checkbox.pack_forget()

                checkboxes[img_id] = {
                    'var': var,
                    'checkbox': checkbox,
                    'filepath': filepath
                }

                col += 1
                if col >= columns:
                    col = 0
                    row += 1
            except Exception as e:
                print(f"Error loading {filepath}: {e}")

def monitor_frame_size():
    global last_frame_width
    current_width = appFrame.winfo_width()
    if current_width != last_frame_width:
        last_frame_width = current_width
        load_photos()
    app.after(100, monitor_frame_size)

def upload_photo():
    if uploadBtn.cget("text") == "Cancel":
        cancel_selection()
        return

    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
    if file_path:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO images (image_path) VALUES (%s)", (file_path,))
        conn.commit()
        conn.close()
        load_photos()

def toggle_select_mode():
    global delete_mode
    delete_mode = not delete_mode

    if delete_mode:
        selectBtn.configure(text="Delete", command=delete_photos)
        for data in checkboxes.values():
            data['checkbox'].pack()
        uploadBtn.configure(text="Cancel")
    else:
        selectBtn.configure(text="Select", command=toggle_select_mode)
        for data in checkboxes.values():
            data['checkbox'].pack_forget()
        uploadBtn.configure(text="Upload")

def delete_photos():
    global delete_mode
    conn = get_db_connection()
    cursor = conn.cursor()

    for img_id, data in checkboxes.items():
        if data['var'].get():
            cursor.execute("DELETE FROM images WHERE id = %s", (img_id,))
    conn.commit()
    conn.close()

    delete_mode = False
    selectBtn.configure(text="Select", command=toggle_select_mode)
    uploadBtn.configure(text="Upload")
    load_photos()

def cancel_selection():
    for data in checkboxes.values():
        data['var'].set(False)
        data['checkbox'].pack_forget()
    uploadBtn.configure(text="Upload")
    selectBtn.configure(text="Select", command=toggle_select_mode)

def monitor_checkboxes():
    if any(data['var'].get() for data in checkboxes.values()):
        uploadBtn.configure(text="Cancel")
    else:
        uploadBtn.configure(text="Upload")
    app.after(100, monitor_checkboxes)

# ==== Inisialisasi Aplikasi ====
app = customtkinter.CTk()
app.geometry("800x650")
app.title("Gallery")
app.bind("<Escape>", handle_escape)  # Bind tombol ESC

header = customtkinter.CTkFrame(app, fg_color="lightblue", height=40)
header.grid_columnconfigure(0, weight=1)
header.grid_columnconfigure(1, weight=0)
header.grid_columnconfigure(2, weight=0)
header.pack(pady=5, fill="x")

header_text = customtkinter.CTkLabel(
    master=header,
    text="My Gallery",
    font=("Arial", 16, "bold"),
    text_color="black",
    anchor="w"
)
header_text.grid(row=0, column=0, padx=10, sticky="w")

uploadBtn = customtkinter.CTkButton(
    master=header,
    text="Upload",
    hover_color="#3b47d1",
    width=100,
    height=30,
    command=upload_photo
)
uploadBtn.grid(row=0, column=1, padx=10, pady=5)

selectBtn = customtkinter.CTkButton(
    master=header,
    text="Select",
    hover_color="#3b47d1",
    width=100,
    height=30,
    command=toggle_select_mode
)
selectBtn.grid(row=0, column=2, padx=10, pady=5)

# Preview Frame (fullscreen)
previewFrame = customtkinter.CTkFrame(app, fg_color="transparent")
previewFrame.pack_forget()

previewImageLabel = customtkinter.CTkLabel(previewFrame, text="")
previewImageLabel.pack(expand=True)

# Grid Frame
appFrame = customtkinter.CTkScrollableFrame(app, width=800, height=800)
appFrame.pack(pady=10, fill="both", expand=True)

last_frame_width = appFrame.winfo_width()

load_photos()
monitor_frame_size()
monitor_checkboxes()

app.mainloop()
