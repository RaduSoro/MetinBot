from threading import Thread, Lock
from utils import Vision, SnowManFilter
import time
import numpy as np
import cv2 as cv


class CaptureAndDetect:

    DEBUG = False

    def __init__(self, metin_window, model_path, hsv_filter, fishbot = False):
        self.metin_window = metin_window
        self.fishbot = fishbot
        self.vision = Vision()
        self.hsv_filter = hsv_filter
        if fishbot:
            self.classifier = None
        else:
            self.classifier = cv.CascadeClassifier(model_path)

        self.screenshot = None
        self.screenshot_time = None

        self.processed_image = None

        self.detection = None
        self.detection_time = None
        self.detection_image = None

        self.stopped = False
        self.lock = Lock()
        # self.vision.init_control_gui() # Uncomment do debug HSV filter

    def start(self):
        self.stopped = False
        if self.fishbot:
            t = Thread(target=self.run_fishbot)
        else:
            t = Thread(target=self.run)
        t.start()

    def run_fishbot(self):
        while not self.stopped:
            # Take screenshot
            screenshot = self.metin_window.capture()
            screenshot_time = time.time()

            self.lock.acquire()
            self.screenshot = screenshot
            self.screenshot_time = screenshot_time
            self.lock.release()

            # Preprocess image for object detection
            processed_img = screenshot

            self.processed_image = processed_img
            # Detect objects
            # Parse results and generate image
            detection_time = time.time()
            detection = None
            detection_image = screenshot.copy()

            top_left = (914, 345)
            bottom_right = (1007, 414)
            self.vision.draw_rectangles_predefined(detection_image,top_left,bottom_right)
            dot_1 = (933,366)
            dot_2 = (981,366)
            dot_3 = (933,400)
            dot_4 = (981,400)
            dots = [dot_1,dot_2,dot_3,dot_4]
            for dot in dots:
                self.vision.draw_dots(detection_image,dot)
            # Acquire lock and set new images
            self.lock.acquire()
            self.detection = detection
            self.detection_time = detection_time
            self.detection_image = detection_image
            self.lock.release()

            if self.DEBUG:
                time.sleep(1)

    def run(self):
        while not self.stopped:
            # Take screenshot
            screenshot = self.metin_window.capture()
            screenshot_time = time.time()

            self.lock.acquire()
            self.screenshot = screenshot
            self.screenshot_time = screenshot_time
            self.lock.release()

            # Preprocess image for object detection
            processed_img = self.vision.apply_hsv_filter(screenshot, hsv_filter=self.hsv_filter)

            self.processed_image = processed_img
            self.vision.black_out_area(processed_img, (350, 271), (676, 461))

            # Detect objects
            output = self.classifier.detectMultiScale2(processed_img,minSize =(100,100))

            # Parse results and generate image
            detection_time = time.time()
            detection = None
            detection_image = screenshot.copy()

            if len(output[0]):
                detection = {'rectangles': output[0], 'scores': output[1]}
                best = self.find_best_match(detection['rectangles'])
                if best is not None:
                    # Used to determine best match via scores
                    # best = detection['rectangles'][np.argmax(detection['scores'])]
                    detection['best_rectangle'] = best
                    detection['click_pos'] = int(best[0] + best[2] / 2), int(best[1] + 0.66 * best[3])
                    self.vision.draw_rectangles(detection_image, detection['rectangles'])
                    self.vision.draw_rectangles(detection_image, [detection['best_rectangle']],
                                                bgr_color=(0, 0, 255))
                    self.vision.draw_marker(detection_image, detection['click_pos'])
                else:
                    continue

            # Acquire lock and set new images
            self.lock.acquire()
            self.detection = detection
            self.detection_time = detection_time
            self.detection_image = detection_image
            self.lock.release()

            if self.DEBUG:
                time.sleep(1)

    def stop(self):
        self.stopped = True

    def get_info(self):
        self.lock.acquire()
        screenshot = None if self.screenshot is None else self.screenshot.copy()
        processed_image = None if self.processed_image is None else self.processed_image.copy()
        screenshot_time = self.screenshot_time
        detection = None if self.detection is None else self.detection.copy()
        detection_time = self.detection_time
        detection_image = None if self.detection_image is None \
            else self.detection_image.copy()
        self.lock.release()
        return screenshot, screenshot_time, detection, detection_time, detection_image, processed_image

    def find_best_match(self, rectangles):
        ideal_width = 300
        diff = []
        for rectangle in rectangles:
            # if self.check_dimensions(rectangle):
            diff.append(abs(rectangle[2] - ideal_width))
        if len(diff) is 0:
            return None
        else:
            return rectangles[np.argmin(diff)]

    def check_dimensions(self,rectangle):
        rectangle = rectangle.copy()
        big_enough = True
        for coord in rectangle:
            if coord - 150 <0 :
                big_enough = False
        return big_enough