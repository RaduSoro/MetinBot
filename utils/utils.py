import os
import pyautogui
import cv2 as cv

def get_metin_needle_path():
    # return 'C:\Users\radus\Desktop\hahahaha\Metin2-Bot-main\utils\needle_metin.png'
    # return cv.imread("484.jpg")
    return 'C:/Users/radus/Desktop/hahahaha/Metin2-Bot-main/utils/484.jpg'

def get_tesseract_path():
    return r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def get_respawn_needle_path():
    return 'C:/Users/radus/Desktop/hahahaha/Metin2-Bot-main/utils/needle_respawn.png'
    # return 'C:/Users/Philipp/Development/Metin2-Bot/utils/needle_respawn.png'

def countdown():
    pyautogui.countdown(3)