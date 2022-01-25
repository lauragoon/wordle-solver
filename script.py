import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import time

from word_logic import gen_words, map_word_scores, get_first_word, next_word, gen_regex, update_greens, update_yellows

DRIVER = None
KEYBOARD_ROWS_TILES = list()
BOARD_ROWS_TILES = list()

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

    # support 3 browsers
    driver = None
    try:
        s = Service(r'geckodriver.exe')
        driver = webdriver.Firefox(service=s)
    except:
        try:
            chromedriver_autoinstaller.install()
            driver = webdriver.Chrome()
        except:
            try:
                driver = webdriver.Edge('msedgedriver')
            except:
                raise NotImplementedError("This script currently supports only Firefox, Chrome, and Edge.")

    driver.get("https://www.powerlanguage.co.uk/wordle/")

    global DRIVER
    DRIVER = driver

    gen_site_globals()

    # close instruction pop-up
    time.sleep(0.6) # delay
    game_app = driver.find_element(By.TAG_NAME, "game-app")
    game = DRIVER.execute_script('return arguments[0].shadowRoot.children', game_app)[1].find_element(By.ID, "game")
    game.click()

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

# Get feedback from previous try
def get_feedback(try_num):
    recent_board_row = BOARD_ROWS_TILES[try_num-1]
    feedback_map = {"green":{}, "yellow":{}, "grey":set()}
    maybe_greys = set()

    for i in range(5):
        curr_tile = recent_board_row[i]
        curr_tile_div = DRIVER.execute_script('return arguments[0].shadowRoot.children', curr_tile)[1]
        curr_tile_state = curr_tile_div.get_attribute("data-state")

        if curr_tile_state == "correct":
            feedback_map["green"][i] = curr_tile.get_attribute("letter")
        elif curr_tile_state == "present":
            feedback_map["yellow"][i] = curr_tile.get_attribute("letter")
        elif curr_tile_state == "absent":
            maybe_greys.add(curr_tile.get_attribute("letter"))
        elif curr_tile_state == "empty":
            raise ReferenceError("Empty tile")
        elif curr_tile_state == "tbd":
            raise ReferenceError("TBD tile")
        else:
            raise ReferenceError("Encountered weird tile state")

    # only add letter to greys if not already counted in green and yellow
    for maybe_grey in maybe_greys:
        if maybe_grey not in feedback_map["green"].values() and maybe_grey not in feedback_map["yellow"].values():
            feedback_map["grey"].add(maybe_grey)

    return feedback_map

# Checker for when word is not in list
def word_not_in_list(try_num):
    recent_board_row = BOARD_ROWS_TILES[try_num-1]
    last_tile = recent_board_row[-1]
    last_tile_div = DRIVER.execute_script('return arguments[0].shadowRoot.children', last_tile)[1]

    return last_tile_div.get_attribute("data-state") == "tbd"

# Determine if game has been won
def game_won(try_num):
    recent_board_row = BOARD_ROWS_TILES[try_num-1]
    correct_so_far = True

    for i in range(5):
        curr_tile = recent_board_row[i]
        curr_tile_div = DRIVER.execute_script('return arguments[0].shadowRoot.children', curr_tile)[1]
        correct_so_far = correct_so_far and curr_tile_div.get_attribute("data-state") == "correct"

    return correct_so_far

# Run helper functions in order
def run_script(refine_word_list=False):

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
    first_tries = set()

    if refine_word_list:
        word_file = open("nonwords.txt", "a")

    while not has_game_finished: # 6 tries
        feedback_regex = gen_regex(greens, yellows, greys)
        yellow_chrs = yellows.values()

        if try_num == 1:
            now_word = get_first_word(first_tries)
        else:
            now_word = next_word(word_scores, feedback_regex, set().union(*yellow_chrs))
        type_word(now_word)

        time.sleep(1.5) # delay so row is updated with feedback before we check

        # won the game
        if game_won(try_num):
            has_game_finished = True
        
        # need to continue the game
        else:
            if word_not_in_list(try_num):
                # if used input starter words, mark it to not try again
                if try_num == 1:
                    first_tries.add(now_word)
                # mark word to not be used in future games
                if refine_word_list:
                    word_file.write('\n' + now_word)
                # delete last word
                for i in range(5):
                    type_keyboard("BACKSPACE")
            else:
                feedback = get_feedback(try_num)
                greens = update_greens(greens, feedback["green"])
                yellows = update_yellows(yellows, feedback["yellow"])
                greys.update(feedback["grey"])
                try_num += 1

            if try_num == 7: # finished try 6
                has_game_finished = True

    if refine_word_list:
        word_file.close()

run_script()