from msilib import type_key
from english_words import english_words_lower_alpha_set
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service

DRIVER = None
KEYBOARD_ROWS_TILES = list()
BOARD_ROWS_TILES = list()

# TODO: case where "word is not in list"

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
def next_word(word_scores, try_num, yellow_chrs=set()):
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
def type_keyboard(click_key):
    key_map = {"q":(0,0), "w":(0,1), "e":(0,2), "r":(0,3), "t":(0,4), "y":(0,5), "u":(0,6), "i":(0,7), "o":(0,8), "p":(0,9),
               "a":(1,0), "s":(1,1), "d":(1,2), "f":(1,3), "g":(1,4), "h":(1,5), "j":(1,6), "k":(1,7), "l":(1,8),
               "z":(2,1), "x":(2,2), "c":(2,3), "v":(2,4), "b":(2,5), "n":(2,6), "m":(2,7),
               "ENTER":(2,0), "BACKSPACE":(2,8)}

    keyboard_location = key_map[click_key]
    KEYBOARD_ROWS_TILES[keyboard_location[0]][keyboard_location[1]].click()

# Type word on keyboard
def type_word(wrd):
    chrs = list(wrd)
    
    for chr in chrs:
        type_keyboard(chr)

    type_keyboard("ENTER")

# Keep track of global variables used to interact with webpage
def gen_site_globals():
    game_app = DRIVER.find_element(By.TAG_NAME, "game-app")
    game_theme_manager = DRIVER.execute_script('return arguments[0].shadowRoot.children', game_app)[1]

    # site keyboard
    keyboard_container = game_theme_manager.find_element(By.ID, "game").find_element(By.TAG_NAME, "game-keyboard")
    keyboard = DRIVER.execute_script('return arguments[0].shadowRoot.children', keyboard_container)[1]
    keyboard_rows = keyboard.find_elements(By.CLASS_NAME, "row")

    keyboard_rows_tiles = []

    for i in range(3):
        curr_keyboard_row = keyboard_rows[i]
        curr_keyboard_tiles = curr_keyboard_row.find_elements(By.TAG_NAME, "button")
        keyboard_rows_tiles.append(curr_keyboard_tiles)
        
    global KEYBOARD_ROWS_TILES
    KEYBOARD_ROWS_TILES = keyboard_rows_tiles

    # input board tiles
    board = game_theme_manager.find_element(By.ID, "game").find_element(By.ID, "board-container").find_element(By.ID, "board")
    board_rows = board.find_elements(By.TAG_NAME, "game-row")

    board_rows_tiles = []

    for i in range(6):
        curr_board_row = board_rows[i]
        curr_board_tiles = DRIVER.execute_script('return arguments[0].shadowRoot.children', curr_board_row)[1].find_elements(By.TAG_NAME, "game-tile")
        board_rows_tiles.append(curr_board_tiles)

    global BOARD_ROWS_TILES
    BOARD_ROWS_TILES = board_rows_tiles

# Connect with webpage
def connect_site():
    s = Service(r'C:\Users\goonl\geckodriver-v0.30.0-win64\geckodriver.exe')
    driver = webdriver.Firefox(service=s)
    driver.get("https://www.powerlanguage.co.uk/wordle/")

    global DRIVER
    DRIVER = driver

    gen_site_globals()

    # close instruction pop-up
    game_app = driver.find_element(By.TAG_NAME, "game-app")
    game_app.click()

# Determine if game has been won
def game_won(try_num):
    recent_board_row = BOARD_ROWS_TILES[try_num-1]
    last_tile = recent_board_row[-1]
    last_tile_div = DRIVER.execute_script('return arguments[0].shadowRoot.children', last_tile)[1]
    correct_so_far = True

    for i in range(5):
        correct_so_far = correct_so_far and last_tile_div.get_attribute("data-state") == "correct"

    return correct_so_far

# Checker for when word is not in list
def word_not_in_list(try_num):
    recent_board_row = BOARD_ROWS_TILES[try_num-1]
    last_tile = recent_board_row[-1]
    last_tile_div = DRIVER.execute_script('return arguments[0].shadowRoot.children', last_tile)[1]

    return last_tile_div.get_attribute("data-state") == "tbd"

# Run helper functions in order
def run_script():

    # pre-game prep
    curr_words = gen_words()
    word_scores = map_word_scores(curr_words)
    connect_site()
    
    # game
    has_game_finished = False
    try_num = 1

    while not has_game_finished: # 6 tries
        now_word = next_word(word_scores, try_num)
        type_word(now_word)

        # won the game
        if game_won(try_num):
            has_game_finished = True
        
        # need to continue the game
        else:
            if not word_not_in_list(try_num):
                try_num += 1
            else:
                for i in range(5): # delete last word
                    type_keyboard("BACKSPACE")

            if try_num == 7: # finished try 6
                has_game_finished = True

run_script()