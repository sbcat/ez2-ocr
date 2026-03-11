import os
import cv2
import easyocr
import numpy as np
import pandas as pd
from thefuzz import fuzz
from thefuzz import process

import constants as c
import params

def calc_grade(rate):
    # calculates grade from rate
    if 0 <= rate < 50:
        grade = 'F'
    elif 50 <= rate < 60:
        grade = 'D'
    elif 60 <= rate < 70:
        grade = 'C'
    elif 70 <= rate < 80:
        grade = 'B'
    elif 80 <= rate < 85:
        grade = 'A'
    elif 85 <= rate < 90:
        grade = 'A+'
    elif 90 <= rate < 93:
        grade = 'S'
    elif 93 <= rate < 95:
        grade = 'S+'
    elif 95 <= rate < 98:
        grade = 'S++'
    elif 98 <= rate < 100:
        grade = 'S+++'
    elif rate == 100:
        grade = 'S++++'
    else:
        grade = ''
        print("grade could not be calculated")
    return grade


def find_mode(img): 
    """
    finds mode text in top-right corner
    mode text finicky to read because it's white on white, needs special processing
    thresholding then gaussian blurring seems to OCR it well enough
    """
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # boosting max brightness up to 255 if not already
    _, max_val, _, _, = cv2.minMaxLoc(img)
    if max_val < 255:
        img = img + (255 - max_val)
        img = cv2.convertScaleAbs(img)

    _, img = cv2.threshold(img, params.MODE_THRESHOLD, 255, cv2.THRESH_BINARY)
    img = cv2.GaussianBlur(img, (3, 3), 0) 
    reader = easyocr.Reader(['en'])
    # allowing only possible characters
    result = reader.readtext(img, detail=0, allowlist='57104K STANDRMICOUEHNBLY') 
    mode_text = result[0]

    # some string substitutions to catch edge cases, number of keys sometimes gets read as letters 
    if mode_text.startswith('I'): 
        mode_text = mode_text.replace('I','1',1)
    elif mode_text.startswith('LK'):
        mode_text = mode_text.replace('L','14',1)
    elif mode_text.startswith('MK'):
        mode_text = mode_text.replace('M','14',1)
    elif mode_text.startswith('VK'):
        mode_text = mode_text.replace('V','14',1)
    elif mode_text.startswith('SK'):
        mode_text = mode_text.replace('S','5',1)
    elif mode_text.startswith('EK'):
        mode_text = mode_text.replace('E','5',1)
    elif mode_text.startswith('KK'):
        mode_text = mode_text.replace('K','7',1)

    # fuzzy matching text against list of modes, extractOne returns (text, match score) tuple 
    mode = process.extractOne(mode_text, list(c.MODES)) 
    # sometimes minimum score is met despite not finding key number, returns wrong mode
    # explicitly checking first two characters to verify
    if (mode[1] >= params.FUZZY_MATCH_MIN_SCORE and
        (mode_text[:2] in ('5K','7K','10','14') or
        mode[0] in ('CATCH','TURNTABLE'))
    ):
        return mode[0]
    
    print("mode not found")


def find_title(img, mode):
    """
    reads song title, level, difficulty
    """
    reader = easyocr.Reader(['en', 'ko'])
    results = reader.readtext(img, detail=0)
    info = {}
    # parsing results can be tricky, songs having subtitles split across multiple strings
    info['title'] = ''
    for result in results:
        if result.isdigit() and len(result) <= 2:
            info['level'] = result
            continue
        # space in difficulty name often not read, fuzzy matching without it
        diff_match = process.extractOne(result.replace(' ',''), (diff.replace(' ','') for diff in list(c.DIFFICULTIES)))
        if diff_match[1] >= params.FUZZY_MATCH_MIN_SCORE:
            # inserting space back into difficulty
            info['difficulty'] = diff_match[0][:-3] + ' ' + diff_match[0][-3:]
            continue
        info['title'] += result + ' '

    # uses different scorer since subtitle words can be out of order
    title_match = process.extractOne(info['title'], c.SONGS, scorer=fuzz.token_sort_ratio)
    if title_match[1] >= params.TITLE_MATCH_MIN_SCORE:
        info['title'] = title_match[0]
    else:
        # kamui and 天地開闢 only titles to not use latin or korean characters, checking for them separately
        cnreader = easyocr.Reader(['ch_tra'])
        cntitle = cnreader.readtext(img, detail=0, allowlist='神威天地開闢')
        if cntitle[0] in ('神威','天地開闢'):
            info['title'] = cntitle[0]
        else:
            print("no title found")

    # checking for skull difficulty
    if (info['title'], info['difficulty'], mode) in c.SKULLS:
        info['level'] = 21

    return info


def find_chart_info_course(img, mode):
    """
    reads song title + course name
    """
    reader = easyocr.Reader(['en', 'ko'])
    results = reader.readtext(img, detail=0)
    info = {}
    coursedata = pd.read_csv(os.path.join('data', mode.lower().replace(' ',''))) 


def find_score_values(img):
    """
    finds score values, and derives grade/all combo/all cool
    fairly reliable with just image erosion and limiting OCR to numbers
    """
    kernel = np.ones((2, 2), np.uint8) 
    img = cv2.erode(img, kernel)
    reader = easyocr.Reader(['en'])
    results = reader.readtext(img, detail=0, allowlist='0123456789.')
    values = {}
    # results should contain 9 numbers for all modes except catch
    if len(results) == 9:
        for idx, value in enumerate(c.SCORE_VALUE_NAMES):
            # rate at index 6
            if idx != 6:
                values[value] = int(results[idx])
            # rate needs to be float not int
            # % in rate often gets read as number, remove it if it exists
            else:
                values[value] = float(results[idx][:5])
        
        values['grade'] = calc_grade(values['rate'])
        # logic to determine all combo + all cool
        if values['total_notes'] == values['max_combo']:
            values['all_combo'] = True
            if values['GOOD'] == 0:
                values['all_cool'] = True
        else:
            values['all_combo'] = False
        # defaults to false if not set to true earlier
        values['all_cool'] = values.get('all_cool', False) 
        return values
    
    # catch gets read here
    elif len(results) == 6:
        for idx, value in enumerate(c.SCORE_VALUE_NAMES_CATCH):
            # rate at index 3 this time
            if idx != 3:
                values[value] = int(results[idx])
            else:
                values[value] = float(results[idx][:5])
        
        values['grade'] = calc_grade(values['rate'])
        if values['total_notes'] == values['CATCH']:
            values['all_combo'] = True
            values['all_cool'] = True
        return values

    print("score values not read correctly")


def find_effectors(img, mode):
    """
    finding random + auto effectors with template matching
    pretty reliable but scaling needs to be exact
    """
    img = cv2.resize(img, (640, 480)) 
    effectors = {}
    for effectortype in ('random','auto'):
        bestmatch = ('', 0)
        for effector in os.listdir(os.path.join('resources/effectors', effectortype)):
            template = cv2.imread(os.path.join('resources/effectors', effectortype, effector))
            result =  cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            if max_val > bestmatch[1]:
                bestmatch = (effector, max_val)
        # trim off file extension
        effectors[effectortype] = bestmatch[0][:-4] 

    # can use effectors unique to some modes to verify they're are correct
    if (effectors['auto'] == 'Auto Disabled' and mode not in ('5K ONLY', 'CATCH')
        or effectors['random'] == 'F Random' and mode not in ('7K STANDARD', '7K COURSE', '10K MANIAC', '10K COURSE')
        or effectors['auto'] in ('Auto S OFF', 'LS Auto', 'RS Auto') and mode not in ('14K MANIAC', '14K COURSE')
        or effectors['auto'] == 'Mode Switch OFF' and mode not in ('TURNTABLE')
        ):
        print ('Effector not compatible with mode, something isn\'t correct')

    # 14K uses different effector icon for auto off because of no pedal
    if effectors['auto'] == 'Auto S OFF':
            effectors['auto'] = 'Auto OFF' 
    if effectors['auto'] == 'Mode Switch OFF':
            effectors['auto'] = 'Auto OFF' 

    return effectors