from english_words import english_words_lower_alpha_set
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service

# Keep a set of only 5-letter-ed words
def gen_words():
    return set(filter(lambda wrd: len(wrd) == 5 and str.isalpha(wrd), english_words_lower_alpha_set))

# Score words based on frequency of letter appearances
# TODO: de-prioritize words with double letters for first word?
def map_word_scores(curr_words):
    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    # letter frequency mapping
    letter_score = {}
    for i in range(26):
        letter_score[alphabet[i]] = 0

    for wrd in curr_words:
            wrd_split = list(wrd)
            for chr in wrd_split:
                letter_score[chr] += 1

    # word frequency mapping
    word_scores = {}
    for wrd in curr_words:
        word_scores[wrd] = 0
        wrd_split = list(wrd)
        for chr in wrd_split:
            word_scores[wrd] += letter_score[chr]

    # set to global for future reference
    return word_scores

# Get word with highest score with given conditions
# TODO: more efficient on yellow chrs
def next_word(word_scores, yellow_chrs=set()):
    found_word = False
    ret_word = ""

    while not found_word:
        curr_word = max(word_scores.items(), key=lambda tup: tup[1])[0]
        if bool(re.match("[a-z][a-z][a-z][a-z][a-z]", curr_word)) and len(set(list(curr_word)).intersection(set(yellow_chrs))) == len(yellow_chrs):
            ret_word = curr_word
            found_word = True
        else:
            del word_scores[curr_word]

    return ret_word

# Type on webpage keyboard
def type_keyboard(keyboard_rows_tiles, click_key):
    key_map = {"q":(0,0), "w":(0,1), "e":(0,2), "r":(0,3), "t":(0,4), "y":(0,5), "u":(0,6), "i":(0,7), "o":(0,8), "p":(0,9),
               "a":(1,0), "s":(1,1), "d":(1,2), "f":(1,3), "g":(1,4), "h":(1,5), "j":(1,6), "k":(1,7), "l":(1,8),
               "z":(2,1), "x":(2,2), "c":(2,3), "v":(2,4), "b":(2,5), "n":(2,6), "m":(2,7),
               "ENTER":(2,0), "BACKSPACE":(2,8)}

    keyboard_location = key_map[click_key]
    keyboard_rows_tiles[keyboard_location[0]][keyboard_location[1]].click()

# Interact with webpage
def interact_site(first_word):
    s = Service(r'C:\Users\goonl\geckodriver-v0.30.0-win64\geckodriver.exe')
    driver = webdriver.Firefox(service=s)
    driver.get("https://www.powerlanguage.co.uk/wordle/")

    # close instruction pop-up
    game_app = driver.find_element(By.TAG_NAME, "game-app")
    game_app.click()

    game_theme_manager = driver.execute_script('return arguments[0].shadowRoot.children', game_app)[1]

    # type
    keyboard_container = game_theme_manager.find_element(By.ID, "game").find_element(By.TAG_NAME, "game-keyboard")
    keyboard = driver.execute_script('return arguments[0].shadowRoot.children', keyboard_container)[1]
    keyboard_rows = keyboard.find_elements(By.CLASS_NAME, "row")

    keyboard_rows_tiles = []

    for i in range(3):
        curr_keyboard_row = keyboard_rows[i]
        curr_keyboard_tiles = curr_keyboard_row.find_elements(By.TAG_NAME, "button")
        keyboard_rows_tiles.append(curr_keyboard_tiles)

    type_keyboard(keyboard_rows_tiles, first_word[0])
    type_keyboard(keyboard_rows_tiles, first_word[1])
    type_keyboard(keyboard_rows_tiles, first_word[2])
    type_keyboard(keyboard_rows_tiles, first_word[3])
    type_keyboard(keyboard_rows_tiles, first_word[4])
    type_keyboard(keyboard_rows_tiles, "ENTER")

    # TODO: case where "word is not in list"


# Run helper functions in order
def run_script():

    # pre-game prep
    curr_words = gen_words()
    word_scores = map_word_scores(curr_words)
    
    # game
    first_word = next_word(word_scores)
    interact_site(first_word)

run_script()