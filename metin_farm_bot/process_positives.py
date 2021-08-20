from utils.window import MetinWindow, OskWindow
import pyautogui
import time
import os
import numpy as np
import cv2 as cv
from utils.samples import Samples



def main():
    pyautogui.countdown(3)
    cwd = os.getcwd()
    print(cwd)
    generate_negative_description_file("./classifier/negative_rf/")
    # generate_positive_description_file("./classifier/positive/")
    # size = (20, 32)
    # samples = Samples('pos.txt', desired_size=size)
    # samples.display_images(resized=True)
    # # samples.generate_negs_from_samples(f'classifier/negs_from_pos_{int(time.time())}')
    # samples.export_samples(f'classifier/sample_export_{int(time.time())}', resized=True)


    print('Done')



def generate_negative_description_file(folder):
    # open the output file for writing. will overwrite all existing data in there
    with open('neg_rf.txt', 'w') as f:
        # loop over all the filenames
        for filename in os.listdir(folder):
            f.write(folder + filename + '\n')


def generate_positive_description_file(folder):
    # open the output file for writing. will overwrite all existing data in there
    with open('pos.txt', 'w') as f:
        # loop over all the filenames
        for filename in os.listdir(folder):
            f.write(folder + filename + '\n')
if __name__ == '__main__':
    main()

