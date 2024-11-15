import cv2 as cv
import mediapipe as mp
import numpy as np
import pyautogui as pg
import math  # Untuk menghitung jarak antara dua titik

cam = cv.VideoCapture(0)

mphands = mp.solutions.hands
hands = mphands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

screenWidth, screenHeight = pg.size()  # Ukuran layar
aspect_ratio = screenWidth / screenHeight  # Rasio layar
print(f"Screen size: {screenWidth}x{screenHeight}, Aspect ratio: {aspect_ratio:.2f}")

frame_margin = 100  # Margin untuk membatasi area gerak
tipid = [4, 8, 12, 16, 20]  # ID ujung jari sesuai MediaPipe

# Variabel untuk pergerakan kursor yang halus
prevX, prevY = 0, 0
smooth_factor = 0.2  # Nilai 0-1, semakin kecil semakin halus

while True:
    success, img = cam.read()
    img = cv.flip(img, 1)
    h, w, c = img.shape
    imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    # Menyesuaikan ukuran persegi panjang berdasarkan rasio layar
    if aspect_ratio > 1:  # Layar lebar (landscape)
        rect_w = w - frame_margin * 2
        rect_h = int(rect_w / aspect_ratio)
    else:  # Layar tinggi (portrait)
        rect_h = h - frame_margin * 2
        rect_w = int(rect_h * aspect_ratio)
    
    x1 = (w - rect_w) // 2
    y1 = (h - rect_h) // 2
    x2 = x1 + rect_w
    y2 = y1 + rect_h

    # Menampilkan area batas pergerakan
    cv.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLms, mphands.HAND_CONNECTIONS)
            lmlist = []
            for id, landmark in enumerate(handLms.landmark):
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                lmlist.append([id, cx, cy])

            # Periksa apakah kelima jari terangkat
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

            # Fungsi Klik Kiri: Deteksi sentuhan antara jempol dan telunjuk
            thumb_tip = lmlist[tipid[0]]  # Ujung jempol
            index_tip = lmlist[tipid[1]]  # Ujung telunjuk
            distance = math.hypot(index_tip[1] - thumb_tip[1], index_tip[2] - thumb_tip[2])
            
            if distance < 20:  # Ambang batas jarak (20 piksel atau lebih kecil untuk memastikan jari bersentuhan)
                cv.circle(img, (index_tip[1], index_tip[2]), 10, (0, 255, 0), cv.FILLED)
                pg.click()  # Klik kiri
                pg.sleep(0.2)  # Tambahkan sedikit jeda untuk menghindari klik berulang terlalu cepat

            # Kursor bergerak hanya jika jari telunjuk dan jempol terdeteksi
            if fingers[0] == 1 and fingers[1] == 1:  # Cek jika telunjuk dan jempol terangkat
                cursor_active = True
                cv.circle(img, (lmlist[8][1], lmlist[8][2]), 10, (255, 0, 0), cv.FILLED)

                # Hitung posisi kursor berdasarkan kedua jari (telunjuk dan jempol)
                X = np.interp(lmlist[8][1], (x1, x2), (0, screenWidth))
                Y = np.interp(lmlist[8][2], (y1, y2), (0, screenHeight))
                
                # Pergerakan halus dengan EMA
                smoothX = prevX + (X - prevX) * smooth_factor
                smoothY = prevY + (Y - prevY) * smooth_factor

                pg.moveTo(smoothX, smoothY, duration=0.01)
                prevX, prevY = smoothX, smoothY  # Update posisi terakhir
            else:
                cursor_active = False
    else:
        cursor_active = False

    # Tetap pada posisi terakhir jika jari tidak terdeteksi
    if not cursor_active:
        prevX, prevY = pg.position()

    cv.imshow("Webcam", img)

    if cv.waitKey(1) & 0xFF == ord('d'):  # Tekan 'd' untuk keluar
        break

cam.release()
cv.destroyAllWindows()
