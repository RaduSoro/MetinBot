import cv2 as cv
import utils
from metin_farm_bot.captureAndDetect import CaptureAndDetect
from utils.window import MetinWindow
from metin_farm_bot.bot import MetinFarmBot
import tkinter as tk
from utils.vision import SnowManFilter, SnowManFilterRedForest, NepheriteFilter, RuinForestFilter, NormalFilter
from functools import partial
from fishbot.fishbot import  MetinFishBot
import sys

global system_stop

def main():
    # Choose which metin
    system_stop = False
    metin_selection = {'metin': None}
    metin_select(metin_selection)
    metin_selection = metin_selection['metin']

    print(metin_selection)
    # extra
    # metin_selection = "lv_90"
    # hsv_filter = SnowManFilter() if metin_selection != 'lv_90' else SnowManFilterRedForest()
    # Countdown
    utils.countdown()

    # Get window and start window capture
    metin_window = MetinWindow('Aeldra')

    if metin_selection is "lv_105":
        hsv_filter = NepheriteFilter()
        capt_detect = CaptureAndDetect(metin_window, 'classifier/cascade/cascade.xml', hsv_filter)
    if metin_selection is "lv_90":
        hsv_filter = RuinForestFilter()
        capt_detect = CaptureAndDetect(metin_window, 'classifier/cascade_rf/cascade.xml', hsv_filter)
    if metin_selection is "fishbot":
        hsv_filter = NormalFilter()
        capt_detect = CaptureAndDetect(metin_window, '', hsv_filter, fishbot= True)


    # Initialize the bot
    if metin_selection is not "fishbot":
        bot = MetinFarmBot(metin_window, metin_selection)
    else:
        bot = MetinFishBot(metin_window, metin_selection)
    capt_detect.start()
    bot.start()

    while not system_stop:

        # Get new detections
        screenshot, screenshot_time, detection, detection_time, detection_image, processed_image = capt_detect.get_info()

        # Update bot with new image
        bot.detection_info_update(screenshot, screenshot_time, detection, detection_time)

        if detection_image is None:
            continue

        # Draw bot state on image
        overlay_image = bot.get_overlay_image()
        detection_image = cv.addWeighted(detection_image, 1, overlay_image, 1, 0)

        # Display image
        if metin_selection is "fishbot":
            cv.imshow('Matches', detection_image)

        # press 'q' with the output window focused to exit.
        # waits 1 ms every loop to process key presses
        key = cv.waitKey(1)

        if key == ord('k'):
            bot.switch_to_calibrated()#calibrated


        if key == ord('q'):
            capt_detect.stop()
            bot.stop()
            cv.destroyAllWindows()
            sys.exit("Pressed q, stopping")
            break

    print('Done.')

def metin_select(metin_selection):
    metins = {'Neptherite': 'lv_105',
              'Red Forest': 'lv_90',
              "Fishbot": "fishbot"}


    def set_metin_cb(window, metin, metin_selection):
        metin_selection['metin'] = metin
        window.destroy()

    window = tk.Tk()
    window.title("STUFF")
    tk.Label(window, text='Select Metin:').pack(pady=5)

    for button_text, label in metins.items():
        tk.Button(window, text=button_text, width=30, command=partial(set_metin_cb, window, label, metin_selection))\
            .pack(padx=3, pady=3)

    window.mainloop()

if __name__ == '__main__':
    main()
