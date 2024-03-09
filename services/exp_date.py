import cv2
import numpy as np
import re
import ollama


def read_text(reader, image_bytes, details=0, paragraph=False):
    """
    Function: read_text

    Parameters:
    - reader: OCR reader object.
    - image_bytes: Bytes of the image.
    - details: Level of detail (0: text only, 1: includes boxes and scores).
    - paragraph: Treats image as single paragraph (True) or separates lines (False).

    Returns:
    - result_text: Recognized text and details.
    """

    nparr = np.frombuffer(image_bytes, np.uint8)
    image_array = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    result_text = reader.readtext(image_array, detail=details, paragraph=paragraph)
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
    matchs = set()
    for pattern in date_patterns:
        match = re.search(pattern, comb_text)
        if match:
            expiry_date = match.group()
            matchs.add(match)
    matchs = list(matchs)
    if len(matchs) > 0:
        return matchs
    return None


async def detect_good_date(dates, model=None):
    # Generate a response to the prompt
    if model is None:
        model = ollama.AsyncClient()
    prompt_template = ('I have the following dates \"{}\" separated by \"|-|\", which may contain a valid expiration '
                       'date. Give me the good date or specify that the no valid expiration date was found. GIVE ME '
                       'THE ANSWER ONLY IN THE FOLLOWING FORMAT \"expiration date: <the expiration date> \" or \"no '
                       'valid expiration date found\"')
    comb_text = "|-|".join(dates)
    response = model.generate('notux', prompt_template.format(comb_text))

    # Return the response
    return await response


def full_exp_date_detection(reader, image_bytes):
    result_texts = read_text(reader, image_bytes, details=0, paragraph=False)
    dates = detect_exp_dates(result_texts)
    good_date = detect_good_date(dates)
    return good_date
