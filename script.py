from english_words import english_words_lower_alpha_set
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import time

DRIVER = None
KEYBOARD_ROWS_TILES = list()
BOARD_ROWS_TILES = list()

# Keep a set of only 5-letter-ed words
def gen_words():
    return set(filter(lambda wrd: len(wrd) == 5 and str.isalpha(wrd), english_words_lower_alpha_set))

# Score words based on frequency of letter appearances
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

    return word_scores

# Get word with highest score with given conditions
def next_word(word_scores, feedback_regex, yellows):
    found_word = False
    ret_word = ""

    while not found_word:

        # get next highest scoring word
        curr_word = max(word_scores.items(), key=lambda tup: tup[1])[0]

        # check if word matches against regex from past feedback
        # also checks if word contains the yellow characters; yellow chars are filtered out of their original index position via the regex
        if bool(re.match(feedback_regex, curr_word)) and len(set(curr_word).intersection(yellows)) == len(yellows):
            ret_word = curr_word
            found_word = True

        # words that don't pass the check don't need to stay in word list anymore
        else:
            del word_scores[curr_word]

    # delete currently guessed word so we don't guess it again
    del word_scores[ret_word]

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
    s = Service(r'geckodriver.exe')
    driver = webdriver.Firefox(service=s)
    driver.get("https://www.powerlanguage.co.uk/wordle/")

    global DRIVER
    DRIVER = driver

    gen_site_globals()

    # close instruction pop-up
    time.sleep(1) # delay
    game_app = driver.find_element(By.TAG_NAME, "game-app")
    game_app.click()

# Determine if game has been won
def game_won(try_num):
    recent_board_row = BOARD_ROWS_TILES[try_num-1]
    correct_so_far = True

    for i in range(5):
        curr_tile = recent_board_row[i]
        curr_tile_div = DRIVER.execute_script('return arguments[0].shadowRoot.children', curr_tile)[1]
        correct_so_far = correct_so_far and curr_tile_div.get_attribute("data-state") == "correct"

    return correct_so_far

# Checker for when word is not in list
def word_not_in_list(try_num):
    recent_board_row = BOARD_ROWS_TILES[try_num-1]
    last_tile = recent_board_row[-1]
    last_tile_div = DRIVER.execute_script('return arguments[0].shadowRoot.children', last_tile)[1]

    return last_tile_div.get_attribute("data-state") == "tbd"

# Get feedback from previous try
def get_feedback(try_num):
    recent_board_row = BOARD_ROWS_TILES[try_num-1]
    feedback_map = {"green":{}, "yellow":{}, "grey":set()}

    for i in range(5):
        curr_tile = recent_board_row[i]
        curr_tile_div = DRIVER.execute_script('return arguments[0].shadowRoot.children', curr_tile)[1]
        curr_tile_state = curr_tile_div.get_attribute("data-state")

        if curr_tile_state == "correct":
            feedback_map["green"][i] = curr_tile.get_attribute("letter")
        elif curr_tile_state == "present":
            feedback_map["yellow"][i] = curr_tile.get_attribute("letter")
        elif curr_tile_state == "absent":
            feedback_map["grey"].add(curr_tile.get_attribute("letter"))
        elif curr_tile_state == "empty":
            raise ReferenceError("Empty tile")
        elif curr_tile_state == "tbd":
            raise ReferenceError("TBD tile")
        else:
            raise ReferenceError("Encountered weird tile state")

    return feedback_map

# Generate the regex based on feedback of letters
def gen_regex(greens, yellows, greys):
    ret_regex = ["","","","",""]

    # fill in correct letters
    for itm in greens.items():
        idx = itm[0]
        letter = itm[1]
        ret_regex[idx] = "(?:[" + letter + "])"
    
    # fill in rest
    for i in range(5):

        # not found correct letter for this idx yet
        if len(ret_regex[i]) == 0:

            dont_include = set()
            dont_include.update(greys)

            if i in yellows.keys():
                letters = yellows[i]
                dont_include.update(letters)

            if len(dont_include) > 0:
                dont_include_letters = "".join(dont_include)
                ret_regex[i] = "(?:(?![" + dont_include_letters + "])[a-z])"
            else:
                ret_regex[i] = "(?:[a-z])"

    return "".join(ret_regex)

# Update data structure for greens/corrects
def update_greens(greens, green_feedback):
    for itm in green_feedback.items():
        idx = itm[0]
        letter = itm[1]

        if idx not in greens.keys():
            greens[idx] = letter

    return greens

# Update data structure for yellows/presents
def update_yellows(yellows, yellow_feedback):
    for itm in yellow_feedback.items():
        idx = itm[0]
        letter = itm[1]

        if idx not in yellows.keys():
            yellows[idx] = set()
        yellows[idx].add(letter)

    return yellows

# Run helper functions in order
def run_script():

    # pre-game prep
    curr_words = gen_words()
    word_scores = map_word_scores(curr_words)
    connect_site()

    time.sleep(0.5) # delay so don't start typing before site loads
    
    # game
    has_game_finished = False
    try_num = 1
    greens = {} # int : str
    yellows = {} # int : set(str)
    greys = set()

    while not has_game_finished: # 6 tries
        feedback_regex = gen_regex(greens, yellows, greys)
        yellow_chrs = yellows.values()
        now_word = next_word(word_scores, feedback_regex, set().union(*yellow_chrs))
        type_word(now_word)

        time.sleep(1.7) # delay so row is updated with feedback before we check

        # won the game
        if game_won(try_num):
            has_game_finished = True
        
        # need to continue the game
        else:
            if word_not_in_list(try_num):
                for i in range(5): # delete last word
                    type_keyboard("BACKSPACE")
            else:
                feedback = get_feedback(try_num)
                greens = update_greens(greens, feedback["green"])
                yellows = update_yellows(yellows, feedback["yellow"])
                greys.update(feedback["grey"])
                try_num += 1

            if try_num == 7: # finished try 6
                has_game_finished = True

run_script()