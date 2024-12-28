import cv2 as cv
import mediapipe as mp
import numpy as np
import pyautogui as pg
import math
import threading
import customtkinter
from tkinter import filedialog
from PIL import Image
import os

folder = "gallery_photos"
checkboxes = {}
delete_mode = False  # Untuk melacak apakah dalam mode delete
# hand_tracking_active = True  # Mengontrol status hand tracking

# --- Bagian MediaPipe untuk Deteksi Tangan ---
def hand_tracking():
    # Inisialisasi kamera dan modul MediaPipe
    cam = cv.VideoCapture(0)
    mphands = mp.solutions.hands
    hands = mphands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
    mpDraw = mp.solutions.drawing_utils

    screenWidth, screenHeight = pg.size()  # Ukuran layar
    aspect_ratio = screenWidth / screenHeight
    print(f"Screen size: {screenWidth}x{screenHeight}, Aspect ratio: {aspect_ratio:.2f}")

    frame_margin = 100  # Margin untuk area gerak
    tipid = [4, 8, 12, 16, 20]  # ID ujung jari sesuai MediaPipe

    # Variabel untuk pergerakan kursor yang halus
    prev_positions = {"Right": (0, 0), "Left": (0, 0)}
    smooth_factor = 0.1  # Semakin kecil nilai, semakin halus

    # Variabel untuk scroll
    scroll_speed = 200  # Kecepatan scroll

    scale_factor_x = 0.5
    scale_factor_y = 0.5

    while True:
        # if not hand_tracking_active:
        #     continue  # Hentikan hand tracking jika tidak aktif
        success, img = cam.read()
        img = cv.flip(img, 1)
        h, w, c = img.shape
        imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        # Menyesuaikan ukuran persegi panjang berdasarkan rasio layar
        if aspect_ratio > 1:
            rect_w = w - frame_margin * 2
            rect_h = int(rect_w / aspect_ratio)
        else:
            rect_h = h - frame_margin * 2
            rect_w = int(rect_h * aspect_ratio)

        x1 = (w - rect_w) // 2
        y1 = (h - rect_h) // 2
        x2 = x1 + rect_w
        y2 = y1 + rect_h

        cv.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

        if results.multi_hand_landmarks and results.multi_handedness:
            for idx, handLms in enumerate(results.multi_hand_landmarks):
                # Tentukan apakah tangan kanan atau kiri
                hand_label = results.multi_handedness[idx].classification[0].label  # "Right" atau "Left"
                mpDraw.draw_landmarks(img, handLms, mphands.HAND_CONNECTIONS)

                lmlist = []
                for id, landmark in enumerate(handLms.landmark):
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    lmlist.append([id, cx, cy])

                # Deteksi jari terangkat
                fingers = []
                if lmlist[tipid[0]][1] < lmlist[tipid[0] - 2][1]:  # Jempol
                    fingers.append(1)
                else:
                    fingers.append(0)

                for id in range(1, 5):  # Telunjuk hingga kelingking
                    if lmlist[tipid[id]][2] < lmlist[tipid[id] - 3][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                
                thumb_tip = lmlist[tipid[0]]    # Ujung jari jempol
                index_tip = lmlist[tipid[1]]    # Ujung jari telunjuk
                middle_tip = lmlist[tipid[2]]   # Ujung jari tengah
                
                # Fungsi Klik Kiri: Jempol dan Telunjuk menyentuh
                distance_index_thumb = math.hypot(index_tip[1] - thumb_tip[1], index_tip[2] - thumb_tip[2])
                # Fungsi Klik Kanna: Jempol dan Tengah menyentuh
                distance_middle_thumb = math.hypot(middle_tip[1] - thumb_tip[1], middle_tip[2] - thumb_tip[2])

                if distance_index_thumb < 20:  # Klik Kiri
                    cv.putText(img, 'Klik Kiri', (w - 200, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
                    cv.circle(img, (index_tip[1], index_tip[2]), 10, (0, 255, 0), cv.FILLED)
                    pg.click()
                    pg.sleep(0.2)
                    
                if distance_middle_thumb < 20:  # Klik Kanan
                    cv.putText(img, 'Klik Kanan', (w - 200, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
                    cv.circle(img, (index_tip[1], index_tip[2]), 10, (0, 255, 0), cv.FILLED)
                    pg.rightClick()
                    pg.sleep(0.2)
                
                # Scroll: Jika tiga jari terangkat (telunjuk, tengah, manis)
                if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
                    if lmlist[tipid[1]][2] < h // 2:
                        cv.putText(img, 'Scroll ke atas', (w - 300, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
                        pg.scroll(scroll_speed)  # Scroll ke atas
                    else:
                        cv.putText(img, 'Scroll ke bawah', (w - 300, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
                        pg.scroll(-scroll_speed)  # Scroll ke bawah

                # Kursor bergerak jika telunjuk dan jempol terangkat untuk masing-masing tangan
                if hand_label == "Right":
                    cv.putText(img, f'{hand_label} Hand', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv.LINE_AA)
                    thumb_up = lmlist[tipid[0]][1] < lmlist[tipid[0] - 2][1]  # Posisi jempol
                    index_up = lmlist[tipid[1]][2] < lmlist[tipid[1] - 2][2]  # Posisi telunjuk
                    other_fingers_down = all(lmlist[tipid[i]][2] > lmlist[tipid[i] - 2][2] for i in range(2, 5))  # Jari lainnya turun

                    if thumb_up and index_up and other_fingers_down:
                        cv.circle(img, (lmlist[8][1], lmlist[8][2]), 10, (255, 0, 0), cv.FILLED)

                        # Interpolasi jangkauan gerak tangan ke seluruh layar
                        X = np.interp(lmlist[8][1], (x1 + int(frame_margin * scale_factor_x), x2 - int(frame_margin * scale_factor_x)), (0, screenWidth))
                        Y = np.interp(lmlist[8][2], (y1 + int(frame_margin * scale_factor_y), y2 - int(frame_margin * scale_factor_y)), (0, screenHeight))

                        # Smooth movement for right hand
                        prevX, prevY = prev_positions["Right"]
                        smoothX = prevX + (X - prevX) * smooth_factor
                        smoothY = prevY + (Y - prevY) * smooth_factor
                        pg.moveTo(smoothX, smoothY, duration=0.01)
                        prev_positions["Right"] = (smoothX, smoothY)

                elif hand_label == "Left":
                    cv.putText(img, f'{hand_label} Hand', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv.LINE_AA)
                    thumb_up = lmlist[tipid[0]][1] > lmlist[tipid[0] - 2][1]  # Posisi jempol
                    index_up = lmlist[tipid[1]][2] < lmlist[tipid[1] - 2][2]  # Posisi telunjuk
                    other_fingers_down = all(lmlist[tipid[i]][2] > lmlist[tipid[i] - 2][2] for i in range(2, 5))  # Jari lainnya turun

                    if thumb_up and index_up and other_fingers_down:
                        cv.circle(img, (lmlist[8][1], lmlist[8][2]), 10, (0, 0, 255), cv.FILLED)

                        # Interpolasi jangkauan gerak tangan ke seluruh layar
                        X = np.interp(lmlist[8][1], (x1 + int(frame_margin * scale_factor_x), x2 - int(frame_margin * scale_factor_x)), (0, screenWidth))
                        Y = np.interp(lmlist[8][2], (y1 + int(frame_margin * scale_factor_y), y2 - int(frame_margin * scale_factor_y)), (0, screenHeight))

                        # Smooth movement for left hand
                        prevX, prevY = prev_positions["Left"]
                        smoothX = prevX + (X - prevX) * smooth_factor
                        smoothY = prevY + (Y - prevY) * smooth_factor
                        pg.moveTo(smoothX, smoothY, duration=0.01)
                        prev_positions["Left"] = (smoothX, smoothY)

# def on_focus_in(event):
#     global hand_tracking_active
#     hand_tracking_active = True  # Aktifkan hand tracking saat aplikasi mendapat fokus

# def on_focus_out(event):
#     global hand_tracking_active
#     hand_tracking_active = False  # Matikan hand tracking saat aplikasi kehilangan fokus

# --- Bagian CustomTkinter untuk Aplikasi Gallery ---
# Fungsi untuk memuat foto dari folder
def load_photos():
    if not os.path.exists(folder):
        os.makedirs(folder)  # Jika folder tidak ada, buat folder

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

    for filename in os.listdir(folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
            filepath = os.path.join(folder, filename)
            try:
                img = Image.open(filepath)
                photo = customtkinter.CTkImage(img, size=(150, 150))

                photo_frame = customtkinter.CTkFrame(appFrame, fg_color="transparent")
                photo_frame.grid(row=row, column=col, padx=padding, pady=padding)

                img_label = customtkinter.CTkLabel(photo_frame, image=photo, text="")
                img_label.image = photo
                img_label.pack()

                var = customtkinter.BooleanVar()
                checkbox = customtkinter.CTkCheckBox(
                    photo_frame, text="", variable=var
                )
                checkbox.pack(pady=5)

                checkboxes[filepath] = {'var': var, 'checkbox': checkbox}

                checkbox.pack_forget()  # Sembunyikan checkbox secara default

                col += 1
                if col >= columns:
                    col = 0
                    row += 1
            except Exception as e:
                print(f"Error loading {filename}: {e}")

# Fungsi untuk memonitor perubahan ukuran frame
def monitor_frame_size():
    global last_frame_width

    current_width = appFrame.winfo_width()

    if current_width != last_frame_width:
        last_frame_width = current_width
        load_photos()

    app.after(100, monitor_frame_size)

# Fungsi untuk mengunggah gambar
def upload_photo():
    if uploadBtn.cget("text") == "Cancel":
        cancel_selection()  # Batalkan semua centangan dan sembunyikan checkbox
        return

    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")]
    )
    if file_path:
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(folder, file_name)
        if not os.path.exists(dest_path):
            Image.open(file_path).save(dest_path)
        load_photos()

# Fungsi untuk toggle mode Select/Delete
def toggle_select_mode():
    global delete_mode
    delete_mode = not delete_mode

    if delete_mode:
        selectBtn.configure(text="Delete", command=delete_photos)
        for data in checkboxes.values():
            data['checkbox'].pack()  # Tampilkan checkbox
        uploadBtn.configure(text="Cancel")
    else:
        selectBtn.configure(text="Select", command=toggle_select_mode)
        for data in checkboxes.values():
            data['checkbox'].pack_forget()  # Sembunyikan checkbox
        uploadBtn.configure(text="Upload")

# Fungsi untuk menghapus foto yang dipilih
def delete_photos():
    global delete_mode

    for filepath, data in checkboxes.items():
        if data['var'].get():
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Error deleting {filepath}: {e}")

    delete_mode = False
    selectBtn.configure(text="Select", command=toggle_select_mode)
    uploadBtn.configure(text="Upload")
    load_photos()

# Fungsi untuk membatalkan semua centangan dan sembunyikan checkbox
def cancel_selection():
    for data in checkboxes.values():
        data['var'].set(False)  # Hapus centangan
        data['checkbox'].pack_forget()  # Sembunyikan checkbox
    uploadBtn.configure(text="Upload")  # Ubah tombol kembali ke Upload
    selectBtn.configure(text="Select", command=toggle_select_mode)

# Fungsi untuk memantau checkbox dan mengubah tombol upload menjadi cancel
def monitor_checkboxes():
    if any(data['var'].get() for data in checkboxes.values()):
        uploadBtn.configure(text="Cancel")
    else:
        uploadBtn.configure(text="Upload")

    app.after(100, monitor_checkboxes)

# Fungsi utama untuk menjalankan GUI dan MediaPipe

# Thread untuk MediaPipe
threading.Thread(target=hand_tracking, daemon=True).start()

# Jalankan aplikasi CustomTkinter
# Inisialisasi aplikasi
app = customtkinter.CTk()
app.geometry("700x600")
app.title("Gallery")

# app.bind("<FocusIn>", on_focus_in)
# app.bind("<FocusOut>", on_focus_out)

header = customtkinter.CTkFrame(
    app, 
    fg_color="lightblue",
    width=700,
    height=40
)
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
uploadBtn.grid(row=0, column=1, padx=10, pady=5, sticky="e")

selectBtn = customtkinter.CTkButton(
    master=header,
    text="Select",
    hover_color="#3b47d1",
    width=100,
    height=30,
    command=toggle_select_mode
)
selectBtn.grid(row=0, column=2, padx=10, pady=5, sticky="e")

appFrame = customtkinter.CTkScrollableFrame(
    app,
    width=700,
    height=800
)
appFrame.pack(pady=10, fill="both", expand=True)

last_frame_width = appFrame.winfo_width()

load_photos()
monitor_frame_size()
monitor_checkboxes()
app.mainloop()
