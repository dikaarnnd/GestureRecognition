import customtkinter
from tkinter import *
from PIL import Image, ImageTk
import os

# Inisialisasi aplikasi
app = customtkinter.CTk()
# app.iconbitmap()
app.geometry("700x700")
app.title("Gallery")

appFrame = customtkinter.CTkScrollableFrame(app,
    width = 300,
    height = 200,
    label_text = "Gallery"
)
appFrame.pack(pady=40)

# for loop untuk btn
for x in range(20):
    customtkinter.CTkButton(appFrame, text="iki baten").pack(pady=20)

# Menjalankan aplikasi
app.mainloop()
