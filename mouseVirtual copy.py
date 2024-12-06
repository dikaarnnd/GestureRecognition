import cv2 as cv
import mediapipe as mp
import numpy as np
import pyautogui as pg
import math
import time  # Tambahan untuk melacak waktu

cam = cv.VideoCapture(0)

mphands = mp.solutions.hands
hands = mphands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
mpDraw = mp.solutions.drawing_utils

screenWidth, screenHeight = pg.size()
aspect_ratio = screenWidth / screenHeight
frame_margin = 100

tipid = [4, 8, 12, 16, 20]

# Variabel pergerakan halus
prevX, prevY = 0, 0
smooth_factor = 0.5

# Variabel untuk fitur double-click
click_start_time = None
click_duration_threshold = 2  # 2 detik untuk double-click

while True:
    success, img = cam.read()
    img = cv.flip(img, 1)
    h, w, c = img.shape
    imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    rect_w = w - frame_margin * 2
    rect_h = int(rect_w / aspect_ratio) if aspect_ratio > 1 else h - frame_margin * 2
    x1, y1 = (w - rect_w) // 2, (h - rect_h) // 2
    x2, y2 = x1 + rect_w, y1 + rect_h

    cv.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLms, mphands.HAND_CONNECTIONS)
            lmlist = [[id, int(landmark.x * w), int(landmark.y * h)] for id, landmark in enumerate(handLms.landmark)]

            fingers = [
                1 if lmlist[tipid[0]][1] < lmlist[tipid[0] - 2][1] else 0,
                *[1 if lmlist[tipid[id]][2] < lmlist[tipid[id] - 3][2] else 0 for id in range(1, 5)]
            ]

            thumb_tip, index_tip = lmlist[tipid[0]], lmlist[tipid[1]]
            distance = math.hypot(index_tip[1] - thumb_tip[1], index_tip[2] - thumb_tip[2])

            # Klik Kiri biasa
            if distance < 20:
                cv.circle(img, (index_tip[1], index_tip[2]), 10, (0, 255, 0), cv.FILLED)
                
                # Inisialisasi atau cek durasi sentuhan
                if click_start_time is None:
                    click_start_time = time.time()
                else:
                    elapsed_time = time.time() - click_start_time
                    if elapsed_time >= click_duration_threshold:
                        pg.doubleClick()  # Klik kiri dua kali
                        click_start_time = None  # Reset setelah double-click
            else:
                click_start_time = None  # Reset jika tidak ada sentuhan

            if fingers[0] == 1 and fingers[1] == 1:
                cursor_active = True
                cv.circle(img, (lmlist[8][1], lmlist[8][2]), 10, (255, 0, 0), cv.FILLED)

                X = np.interp(lmlist[8][1], (x1, x2), (0, screenWidth))
                Y = np.interp(lmlist[8][2], (y1, y2), (0, screenHeight))

                smoothX = prevX + (X - prevX) * smooth_factor
                smoothY = prevY + (Y - prevY) * smooth_factor

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
