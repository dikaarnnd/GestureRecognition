import numpy as np
import cv2 as cv
import pyautogui as pg
import math

# Model CNN
import mediapipe as mp

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
scroll_speed = 50  # Kecepatan scroll
scroll_smooth_factor = 0.2  # Faktor halus untuk scroll

scale_factor_x = 0.5
scale_factor_y = 0.5

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
                cv.putText(img, f'Scrolling ({hand_label})', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv.LINE_AA)
                if lmlist[tipid[1]][2] < h // 2:
                    pg.scroll(scroll_speed)  # Scroll ke atas
                else:
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




    cv.imshow("Webcam", img)

    if cv.waitKey(1) & 0xFF == ord('d'):
        break

cam.release()
cv.destroyAllWindows()
