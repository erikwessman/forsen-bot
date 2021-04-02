import cv2
import pytesseract
import numpy as np
import re

#set the tessearact path
pytesseract.pytesseract.tesseract_cmd = './.apt/usr/bin/tesseract'

def get_timer(img_path):
    """
    Looks at a screenshot of the stream and finds the timer
    Uses openCV to make the image easier for tesseract to interpret
    Tesseract finds the times, returns the timer in a list [minutes, seconds]
    """

    img = cv2.imread(img_path)

    #Crop the image to only look at timer
    img = img[340:340+50, 1100:1100+130]

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray, img_bin = cv2.threshold(gray,128,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    gray = cv2.bitwise_not(img_bin)

    kernel = np.ones((2, 1), np.uint8)
    img = cv2.erode(gray, kernel, iterations=1)
    img = cv2.dilate(img, kernel, iterations=1)

    time_string = pytesseract.image_to_string(img, config='--psm 7 -c tessedit_char_whitelist=0123456789: ').replace('\f', '').replace('\n', '')
    time_list = re.split(':', time_string)
    
    #if time contains anything other than numbers, return empty list
    for time in time_list:
        if not time.isnumeric():
            return []

    #timer is only showing seconds, insert 0 minutes at index 0
    if len(time_list) == 1:
        time_list.insert(0,0)

    return time_list


def check_dragon(image_path):
    """
    Returns true if Forsen is fighting the dragon
    Looks for 'Ender' in 'Ender Dragon' on top of the screen
    """

    #Crop the image to only look at top text
    img = cv2.imread(image_path)
    img = img[0:0+24, 560:560+160]

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray, img_bin = cv2.threshold(gray,128,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    gray = cv2.bitwise_not(img_bin)

    kernel = np.ones((2, 1), np.uint8)
    img = cv2.erode(gray, kernel, iterations=1)
    img = cv2.dilate(img, kernel, iterations=1)

    dragon_string = pytesseract.image_to_string(img, config='--psm 7').replace('\f', '').replace('\n', '')
    return 'Ender' in dragon_string


def run_ongoing(previous_time, current_time):
    """
    Returns true if it has been less than 15 minutes since a tweet
    """

    return ((current_time - previous_time) < 900)


def get_seconds(time_list):
    """
    Takes an array of a timer [minutes, seconds] and returns the total amount of seconds
    """

    minutes = int(time_list[0])
    seconds = int(time_list[1])

    return (minutes*60 + seconds)


def time_passed(time_array, amount):
    """
    Checks if a timer has passed a certain amount of time
    """

    time = get_seconds(time_array)
    return time > get_seconds(amount)
