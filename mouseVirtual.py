import cv2 as cv
import mediapipe as mp
import numpy as np
import pyautogui as pg
import math

# Inisialisasi kamera dan modul MediaPipe
cam = cv.VideoCapture(0)
mphands = mp.solutions.hands
hands = mphands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

screenWidth, screenHeight = pg.size()  # Ukuran layar
aspect_ratio = screenWidth / screenHeight
print(f"Screen size: {screenWidth}x{screenHeight}, Aspect ratio: {aspect_ratio:.2f}")

frame_margin = 100  # Margin untuk area gerak
tipid = [4, 8, 12, 16, 20]  # ID ujung jari sesuai MediaPipe

# Variabel untuk pergerakan kursor yang halus
prevX, prevY = 0, 0
smooth_factor = 0.1  # Semakin kecil nilai, semakin halus

# Variabel untuk scroll
scroll_speed = 50  # Kecepatan scroll
scroll_smooth_factor = 0.2  # Faktor halus untuk scroll

while True:
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

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
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

            # Fungsi Klik Kiri: Jempol dan Telunjuk menyentuh
            thumb_tip = lmlist[tipid[0]]
            index_tip = lmlist[tipid[1]]
            distance = math.hypot(index_tip[1] - thumb_tip[1], index_tip[2] - thumb_tip[2])

            if distance < 20:  # Klik kiri
                cv.circle(img, (index_tip[1], index_tip[2]), 10, (0, 255, 0), cv.FILLED)
                pg.click()
                pg.sleep(0.2)

            # Scroll: Jika tiga jari terangkat (telunjuk, tengah, manis)
            if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
                cv.putText(img, 'Scrolling', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv.LINE_AA)
                if lmlist[tipid[1]][2] < h // 2:
                    pg.scroll(scroll_speed)  # Scroll ke atas
                else:
                    pg.scroll(-scroll_speed)  # Scroll ke bawah

            # Kursor bergerak jika telunjuk dan jempol terangkat
            if fingers[0] == 1 and fingers[1] == 1:
                cursor_active = True
                cv.circle(img, (lmlist[8][1], lmlist[8][2]), 10, (255, 0, 0), cv.FILLED)

                X = np.interp(lmlist[8][1], (x1, x2), (0, screenWidth))
                Y = np.interp(lmlist[8][2], (y1, y2), (0, screenHeight))

                # Smooth movement for cursor
                smoothX = prevX + (X - prevX) * smooth_factor
                smoothY = prevY + (Y - prevY) * smooth_factor

                # Gerakkan kursor ke posisi halus
                pg.moveTo(smoothX, smoothY, duration=0.01)
                prevX, prevY = smoothX, smoothY
            else:
                cursor_active = False
    else:
        cursor_active = False

    if not cursor_active:
        prevX, prevY = pg.position()

    cv.imshow("Webcam", img)

    if cv.waitKey(1) & 0xFF == ord('d'):
        break

cam.release()
cv.destroyAllWindows()