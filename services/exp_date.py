import cv2
#import pytesseract
import re
import cv2
import numpy as np
import re
import ollama
import easyocr
import time
from dateutil.parser import parse
import datetime
eocr_reader = reader = easyocr.Reader(['en'],model_storage_directory='../easy_ocr_models/')  # this needs to run only once to load the model into memory

 
def read_text(image, details=0, paragraph=False):
    """
    Function: read_text

    Parameters:
    - image_bytes: Bytes of the image.
    - details: Level of detail (0: text only, 1: includes boxes and scores).
    - paragraph: Treats image as single paragraph (True) or separates lines (False).

    Returns:
    - result_text: Recognized text and details.
    """

    result_text = eocr_reader.readtext(image, detail=details, paragraph=paragraph)
    return result_text


def detect_exp_dates(text_list):
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY or MM/DD/YY
        r'\d{1,2}-\d{1,2}-\d{2,4}',  # MM-DD-YYYY or MM-DD-YY
        r'\d{2,4}/\d{1,2}/\d{1,2}',  # YYYY/MM/DD or YY/MM/DD
        r'\d{2,4}-\d{1,2}-\d{1,2}',  # YYYY-MM-DD or YY-MM-DD
        r'\d{1,2}\s+\w+\s+\d{2,4}',  # e.g. "12 Jan 2023", "5 April 22"
        r'\w+\s+\d{1,2},?\s+\d{2,4}',  # e.g. "January 12, 2023", "Apr 5, 22"
        r'\d{1,2}\s+\w{3}\s+\d{2,4}',  # e.g. "12 Jan 2023", "5 Apr 22"
        r'\w{3}\s+\d{1,2},?\s+\d{2,4}',  # e.g. "Jan 12, 2023", "Apr 5, 22"
        r'\d{2,4}\.\d{1,2}\.\d{1,2}',  # YYYY.MM.DD
        r'\d{1,2}\.\d{1,2}\.\d{2,4}',  # DD.MM.YYYY or DD.MM.YY
        r'\d{2,4}/\d{1,2}',  # YYYY/MM or YY/MM
        r'\d{1,2}/\d{2,4}',  # MM/YYYY or MM/YY
        r'\d{1,2}\s+\w{3}\.?\s+\d{2,4}',  # e.g. "12 Jan. 2023", "5 Apr 22"
        r'\w{3}\.?\s+\d{1,2},?\s+\d{2,4}',  # e.g. "Jan. 12, 2023", "Apr. 5, 22"
    ]
    comb_text = " ".join(text_list)
    founds = set()
    for pattern in date_patterns:
        match = re.search(pattern, comb_text)
        if match:
            expiry_date = match.group()
            founds.add(expiry_date.strip())
    matchs = list(founds)
    if len(matchs) > 0:
        return matchs
    return None

def check_valid(date):
    d_format = str(date).split('-')
    if int(d_format[1]) > 31 or int(d_format[2]) > 31:
        return False
    c_year = datetime.today().strftime("%Y")
    if abs(int(d_format[0]) - c_year) > 15:
        return False
    return True

def good_date_no_ai(dates):
    if dates is not None:
        for date_string in dates:
            try:
                date = str(parse(date_string)).split(' ')[0]
                print('u',date)
                if check_valid(date):
                    print('valid date:',str(date))
                pass
            except Exception as e:
                pass

def detect_good_date(dates, model=None):
    # Generate a response to the prompt
    if dates is None:
        return "no valid expiration date found"
    if model is None:
        model = ollama.AsyncClient()
    prompt_template = ('I have the following dates \"{}\" separated by \"|-|\", which may contain a valid expiration '
                       'date. Give me the good date or specify that the no valid expiration date was found. GIVE ME '
                       'THE ANSWER ONLY IN THE FOLLOWING FORMAT \"expiration date: <the expiration date> \" or \"no '
                       'valid expiration date found\"')
    comb_text = "|-|".join(dates)
    model = ollama.AsyncClient()
    response = model.generate('notux', prompt_template.format(comb_text))

    # Return the response
    return response['text']


def full_exp_date_detection(image_bytes):
    result_texts = read_text(image_bytes, details=0, paragraph=False)
    dates = detect_exp_dates(result_texts)
    good_date_no_ai(dates)
    # good_date = detect_good_date(dates)
    # return good_date

if __name__ == '__main__':
    # Set up the camera
    cap = cv2.VideoCapture(0)

    # Set the resolution of the camera
    cap.set(3, 640)
    cap.set(4, 480)
    
    # Set the font and scale for OCR
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1

    # Loop to capture images from the camera
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Convert the image to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # print(full_exp_date_detection(gray))
        full_exp_date_detection(gray)

        # Display the image and the recognized expiry date
        cv2.imshow('frame', frame)
        cv2.imshow('processed', gray)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) == ord('q'):
            break

    # Release the camera and close all windows
    cap.release()
    cv2.destroyAllWindows()