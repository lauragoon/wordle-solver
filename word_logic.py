from english_words import english_words_lower_alpha_set
import re
from os.path import exists
import random

# Keep a set of only 5-letter-ed words
def gen_words():
    init_set = set(filter(lambda wrd: len(wrd) == 5 and str.isalpha(wrd), english_words_lower_alpha_set))

    # remove words from non word list if avail
    if exists("non_word_list.txt"):
        with open("non_word_list.txt") as file:
            words = file.readlines()
            words = [word.rstrip().lower() for word in words]

            # remove starter words that have been tried already in prev games
            return set(init_set).difference(set(words))

    else:
        return init_set

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

# Get first word from list
def get_first_word(first_tries):
    # check to see if non word list avail
    non_words = set()
    if exists("non_word_list.txt"):
        with open("non_word_list.txt") as file:
            words = file.readlines()
            words = [word.rstrip().lower() for word in words]
            non_words = set(words)

    # check if start words file exists
    if exists("starters.txt"):
        with open("starters.txt") as file:
            words = file.readlines()
            words = [word.rstrip().lower() for word in words]

            # remove starter words that have been tried already in this game
            words = list(set(words).difference(first_tries))
            
            # only one word to choose from
            if len(words) == 1 and len(words[0]) == 5 and words[0].isalpha() and words[0] not in non_words:
                return words[0]

            # choose random word from list of starters
            elif len(words) > 1:
                while len(words) > 0:
                    chosen_starter = random.choice(words)
                    # check validity of word
                    if len(chosen_starter) == 5 and chosen_starter.isalpha() and chosen_starter not in non_words:
                        return chosen_starter
                    else:
                        words.remove(chosen_starter)
    
    # no valid starter word, go with a default
    return "stare"

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