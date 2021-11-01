import random
from utils.window import MetinWindow, OskWindow
import pyautogui
import sys
import time
import cv2 as cv
from utils.vision import Vision, SnowManFilter, MobInfoFilter
import numpy as np
import enum
from threading import Thread, Lock
import datetime
from utils import * #get_metin_needle_path, get_tesseract_path
import pytesseract
import re
import telegram


class BotState(enum.Enum):
    INITIALIZING = 0
    CALIBRATION = 1
    CALIBRATED = 2
    START_FISH = 3
    FISHING = 4
    CATCHING_FISH = 5
    DEBUG = 101


class MetinFishBot:

    def __init__(self, metin_window, metin_selection):
        self.metin_window = metin_window
        self.metin = metin_selection

        self.osk_window = OskWindow('On-Screen Keyboard')
        self.osk_window.move_window(x=-1495, y=810)

        self.vision = Vision()
        self.mob_info_hsv_filter = MobInfoFilter()

        self.screenshot = None
        self.screenshot_time = None
        self.detection_time = None

        self.overlay_image = None
        self.info_text = ''
        self.delay = None

        self.stopped = False
        self.state_lock = Lock()
        self.info_lock = Lock()
        self.overlay_lock = Lock()

        self.started = time.time()
        self.send_telegram_message('Started')
        self.fishCount = 0
        self.last_error = None

        pytesseract.pytesseract.tesseract_cmd = utils.get_tesseract_path()

        self.time_entered_state = None
        self.state = None
        self.switch_state(BotState.INITIALIZING)
        # self.switch_state(BotState.DEBUG)

    def run(self):
        while not self.stopped:

            if self.state == BotState.INITIALIZING:
                self.metin_window.activate()
                # self.respawn_if_dead()
                self.started = time.time()
                self.switch_state(BotState.CALIBRATION)

            if self.state == BotState.CALIBRATED:
                print("PRESSED K, BOT IS CALIBRATED, STARTING FISH")
                self.switch_state(BotState.START_FISH)

            if self.state == BotState.START_FISH:
                self.metin_window.activate()
                self.reload_bait()
                self.action_fish_rod()
                self.switch_state(BotState.FISHING)

            if self.state == BotState.FISHING:
                previous_reading = {
                    "dot_1": np.array([100, 100, 100]),
                    "dot_2": np.array([100, 100, 100]),
                    "dot_3": np.array([100, 100, 100]),
                    "dot_4": np.array([100, 100, 100])
                }
                pixel_data = self.get_pixel_color(previous_reading)
                #pixel verification timer
                time.sleep(0.1)
                if self.check_sudden_shift(pixel_data):
                    self.switch_state(BotState.CATCHING_FISH)
                # self.switch_state(BotState.DEBUG)

            if self.state == BotState.CATCHING_FISH:
                self.metin_window.activate()
                #time to wait for fish
                sleep_time = random.uniform(1.2,1.4)
                time.sleep(sleep_time)
                self.action_fish_rod()
                time.sleep(random.uniform(3,4.5))
                self.switch_state(BotState.START_FISH)

            if self.state == BotState.DEBUG:
                self.metin_window.activate()
                time.sleep(3)
                # self.rotate_view()
                time.sleep(3)
                while True:
                    self.put_info_text(str(self.metin_window.get_relative_mouse_pos()))
                    time.sleep(1)
                self.stop()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def switch_to_calibrated(self):
        if self.get_state() is BotState.CALIBRATION:
            self.switch_state(BotState.CALIBRATED)

    def detection_info_update(self, screenshot, screenshot_time, result, result_time):
        self.info_lock.acquire()
        self.screenshot = screenshot
        self.screenshot_time = screenshot_time
        self.detection_result = result
        self.detection_time = result_time
        self.info_lock.release()

    def switch_state(self, state):
        self.state_lock.acquire()
        self.state = state
        self.time_entered_state = time.time()
        self.state_lock.release()
        self.put_info_text()

    def get_state(self):
        self.state_lock.acquire()
        state = self.state
        self.state_lock.release()
        return state

    def put_info_text(self, string=''):
        if len(string) > 0:
            self.info_text += datetime.datetime.now().strftime("%H:%M:%S") + ': ' + string + '\n'
        font, scale, thickness = cv.FONT_HERSHEY_SIMPLEX, 0.35, 1
        lines = self.info_text.split('\n')
        text_size, _ = cv.getTextSize(lines[0], font, scale, thickness)
        y0 = 720 - len(lines) * (text_size[1] + 6)

        self.overlay_lock.acquire()
        self.overlay_image = np.zeros((self.metin_window.height, self.metin_window.width, 3), np.uint8)
        self.put_text_multiline(self.overlay_image, self.state.name, 10, 715, scale=0.5, color=(0, 255, 0))
        self.put_text_multiline(self.overlay_image, self.info_text, 10, y0, scale=scale)
        self.overlay_lock.release()

    def get_overlay_image(self):
        self.overlay_lock.acquire()
        overlay_image = self.overlay_image.copy()
        self.overlay_lock.release()
        return overlay_image

    def put_text_multiline(self, image, text, x, y, scale=0.3, color=(0, 200, 0), thickness=1):
        font = font = cv.FONT_HERSHEY_SIMPLEX
        y0 = y
        for i, line in enumerate(text.split('\n')):
            text_size, _ = cv.getTextSize(line, font, scale, thickness)
            line_height = text_size[1] + 6
            y = y0 + i * line_height
            if y > 300:
                cv.putText(image, line, (x, y), font, scale, color, thickness)

    def get_mob_info(self):
        top_left = (756, 13)
        bottom_right = (995, 38)

        self.info_lock.acquire()
        mob_info_box = self.vision.extract_section(self.screenshot, top_left, bottom_right)
        self.info_lock.release()
        random_no = np.random.randint(10101)
        # cv.imwrite(f"./classifier/matches/{random_no}mob_info_box.jpg",mob_info_box)
        mob_info_box = self.vision.apply_hsv_filter(mob_info_box, hsv_filter=self.mob_info_hsv_filter)
        # cv.imwrite(f"./classifier/matches/{random_no}mob_info_box_hsv.jpg",mob_info_box)
        mob_info_text = pytesseract.image_to_string(mob_info_box)
        # print(f"iMAGE TO STriNG {mob_info_text}")
        return self.process_metin_info(mob_info_text)

    def get_pixel_color(self, pixel_data):
        # dot_1 = (933, 366)
        # dot_2 = (981, 366)
        # dot_3 = (933, 400)
        # dot_4 = (981, 400)

        dot_1 = (30,18)
        dot_2 = (63,18)
        dot_3 = (30,63)
        dot_4 = (60,63)
        dots = [dot_1,dot_2,dot_3,dot_4]
        index = 1
        top_left = (914, 345)
        bottom_right = (1007, 414)

        self.info_lock.acquire()
        fish_box = self.vision.extract_section(self.screenshot, top_left, bottom_right)
        self.info_lock.release()

        for dot in dots:
            new_pixel_color = self.vision.extract_pixel_color(fish_box, dot)
            # print(f"index {index} has color : {new_pixel_color[0]} {new_pixel_color[1]} {new_pixel_color[2]}")
            pixel_data[f"dot_{index}_new"] = np.array([new_pixel_color[0],new_pixel_color[1],new_pixel_color[2]])
            index+=1
        return pixel_data

    def check_sudden_shift(self,data):
        counter = 0
        #check of a shift thats bigger or less than 80 on the rgb spectrum on any given channel
        for x in range(1, 5):
            diff = np.subtract(data[f"dot_{x}"],data[f"dot_{x}_new"])
            shifts = diff [(diff>80) | (diff <-80)]
            if len(shifts) > 0:
                counter+=1
        if counter >= 3:
            return True
        else:
            return False

    def calibrate_fish_icon(self):
        top_left = (914,345)
        bottom_right = (1007,414)

        self.info_lock.acquire()
        mob_info_box = self.vision.extract_section(self.screenshot, top_left, bottom_right)
        self.info_lock.release()

    def action_fish_rod(self):
        self.metin_window.activate()
        self.osk_window.press_space()
        time.sleep(random.uniform(0.5, 0.8))

    def reload_bait(self):
        self.metin_window.activate()
        self.osk_window.reload_bait()
        time.sleep(random.uniform(0.1, 0.3))

    def send_telegram_message(self, msg):
        # return
        bot = telegram.Bot(token="1925227114:AAEUiVzZJoWKIQ6BrPYHFNQrddINn1niSeA")
        # print(msg)
        bot.sendMessage(chat_id="1859753003", text=msg)