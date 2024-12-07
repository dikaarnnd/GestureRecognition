def load_photos(frame, folder_path, image_size=(300, 300), padding=10):
    # Hapus widget lama jika ada
    for widget in frame.winfo_children():
        widget.destroy()

    # Dapatkan daftar file gambar dari folder
    file_list = [f for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]

    # Dapatkan lebar aplikasi saat ini
    frame_width = appFrame.winfo_width()
    col_count = max(1, frame_width // (image_size[0] + padding))  # Jumlah kolom

    # Loop untuk membaca file gambar di folder
    row = 0
    col = 0
    for file_name in file_list:
        # Load gambar
        image_path = os.path.join(folder_path, file_name)
        image = customtkinter.CTkImage(
            light_image=Image.open(image_path),
            dark_image=Image.open(image_path),
            size=image_size
        )
        
        # Tambahkan label dengan gambar ke frame
        label = customtkinter.CTkLabel(frame, text="", image=image)
        label.grid(row=row, column=col, padx=padding, pady=padding)

        # Update posisi untuk gambar berikutnya
        col += 1
        if col >= col_count:
            col = 0
            row += 1