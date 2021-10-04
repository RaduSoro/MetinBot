from utils.window import MetinWindow, OskWindow
import pyautogui
import time
import cv2 as cv
from utils.vision import Vision, SnowManFilter, SnowManFilterRedForest, NepheriteFilter, MobInfoFilter, RuinForestFilter


def command_pause():
    time.sleep(0.2)


refPt = []
cropping = False





def main():
    pyautogui.countdown(3)
    aeldra = MetinWindow('Aeldra')
    vision = Vision()
    vision.init_control_gui()
    # sm_filter =
    # sm_filter = NepheriteFilter()/
    # sm_filter = RuinForestFilter()
    # sm_filter = MobInfoFilter()

    count = {'p': 0, 'n': 0}
    while True:
        loop_time = time.time()
        screenshot = aeldra.capture()

        processed_screenshot = vision.apply_hsv_filter(screenshot, hsv_filter=vision.get_hsv_filter_from_controls())
        print(str(aeldra.get_relative_mouse_pos()))
        cv.imshow('Video Feed', processed_screenshot)
        # print(f'{round(1 / (time.time() - loop_time),2)} FPS')

        # press 'q' with the output window focused to exit.
        # waits 1 ms every loop to process key presses
        key = cv.waitKey(1)
        if key == ord('k'):
            cv.destroyAllWindows()
            break
        elif key == ord('p'):
            # r = cv.selectROI("ROI",processed_screenshot)
            # print(r)
            # imCrop = processed_screenshot[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]
            # cv.destroyWindow("ROI")
            # cv.imshow("CROP", imCrop)
            # cv.waitKey(0)
            cv.imwrite('classifier/positive_rf/{}.jpg'.format(int(loop_time)), processed_screenshot)
            count['p'] += 1
            print(f'Saved positive sample. {count["p"]} total.')
        elif key == ord('n'):
            cv.imwrite('classifier/negative_rf/{}.jpg'.format(int(loop_time)), processed_screenshot)
            count['n'] += 1
            print(f'Saved negative sample. {count["n"]} total.')


if __name__ == '__main__':
    main()
