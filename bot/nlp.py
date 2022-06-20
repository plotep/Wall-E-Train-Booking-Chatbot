"""
    Author :            Jamie Grant & Pawel Bielinski
    Files :             nlp.py
    Last Modified :     23/01/22
    Version :           1.4
    Description :       Main language processing file, used to get facts from the user input. The match_facts function
                        is called in the knowledge engine as the base case as the first input option. When there are
                        more facts yielded,the knowledge engine will ask for individual inputs such as what the date is.
                        For this, smaller functions are used such as find_date.

"""

from facts import *
from language_processing import *
import time
from nltk import *
import re
import spacy
import datetime


def match_train_stations(phrase):
    """
    :param phrase: takes in a subtree of words from match_facts
    :return: returns a single string of the TLC of the station that has been found, else an empty string
    """
    station = ""
    temp = []

    for words in phrase:
        if type(words) != type(train_stations[0]):
            words = words.text.lower()
            words = _remove_noise(words)
            temp.append(words)
        else:
            words = _remove_noise(words)
            temp.append(words)
    for i in range(0, len(train_stations)):
        w = train_stations[i]
        w = w.replace(".", " ")
        w = w.replace("'", "")
        w = w.replace("(", "")
        w = w.replace(")", "")
        w = w.split()
        unique = list(set(temp).intersection(w))
        if len(w) == len(unique):
            station = origin_tlc[i - 1]
        if len(unique) > 2:
            station = origin_tlc[i - 1]
    return station


def _remove_noise(input_text):
    """
    :param input_text: string to remove noise from
    :return: string with a subset of words removed
    """
    words = input_text.split()
    noise_free_words = [word for word in words if word not in noise_list]
    noise_free_text = " ".join(noise_free_words)
    return noise_free_text


def has_numbers(input_string):
    """

    :param input_string: string to check for numbers
    :return: bool if contains numbers
    """
    return any(char.isdigit() for char in input_string)


def find_delay_time(time):
    """
    :param time: string to be evaluated if it contains integers, to be used to find time in minutes
    :return: true if string is numeric, else returns None
    """
    if time.isdecimal():
        return time
    else:
        pass


def find_month(month):
    """
    :param month: string that should contain a month in words to find the numeric month
    :return: numeric month , none if not found
    """
    for i in range(len(months)):
        if months[i] == str(month.lower()):
            return i + 1


def is_valid_time(time):
    """

    :param time: string with time in HH:MM format
    :return: bool if time format is correct
    """
    regex = "^([01]?[0-9]|2[0-3]):[0-5][0-9]$";
    p = re.compile(regex);
    if (time == ""):
        return False;
    m = re.search(p, time);
    if m is None:
        return False;
    else:
        return True


def find_time(time):
    """
    :param time: string with time in HH:MM format
    :return: string with time if format is evaluated to be correct, else None
    """
    if is_valid_time(time) is True:
        return time


def find_date(list_of_words):
    """
    :param list_of_words: substring of words from match_facts
    :return: date and time in format 110222 corresponding to 11/02/22 and time in the format HH:MM
    """
    list_of_words_ = []
    for words in list_of_words:
        list_of_words_.append((words.text).lower())

    day = ""
    time = ""
    month = ""
    year = datetime.date.today().year
    year = year.__str__()
    year = year.replace("20", "")

    for words in list_of_words_:
        if has_numbers(words) is True:
            for substring in ending_of_word_numbers:
                if substring in words:
                    day = words.replace(substring, "")
            if words.isdecimal():
                day = words
            if ':' in words:
                time = words.replace(":", "")
        else:
            for i in range(len(months)):
                if words == months[i]:
                    if i < 10:
                        month = "0" + (i + 1).__str__()
                    else:
                        month = (i + 1).__str__()
    if day != "" and int(day) < 10:
        day = "0" + day

    if time != "" and day != "" and time != "":
        date = day + month + year
        return date, time
    if month != "" and day != "" and time == "":
        date = day + month + year
        return date
    if time != "" and month == "" and day == "":
        return time


def get_root_words_to(words, destination_station):
    for tree_words in where_to:
        if tree_words == words.lemma_:
            # sanity check - sometimes long strings in tree can go lump wrong things together
            if (destination_station == ""):
                temp = list(words.subtree)
                temp = match_train_stations(temp)
                if temp != destination_station:
                    destination_station = temp
                    return destination_station
                else:
                    destination_station = ""



def get_root_words_from(words, destination_station, departure_station):
    for tree_words in where_from:
        if tree_words == words.lemma_:
            # sanity check - sometimes long strings in tree can go lump wrong things together
            if (departure_station == ""):
                temp = list(words.subtree)
                temp = match_train_stations(temp)
                if temp != destination_station:
                    departure_station = temp
                    return departure_station
                else:
                    departure_station = ""


def get_root_time(words):
    for tree_words in prepositions_list_time_depart:
        if tree_words == words.lemma_:
            s = list(words.ancestors)
            if s[0].lemma_ not in list(return_list):
                date = list(words.subtree)
                if find_date(date) is not None:
                    return find_date(date)


def get_date(words):
    for tree_words in prepositions_list_time_depart:
        if tree_words == words.lemma_:
            date = list(words.subtree)
            if find_date(date) is not None:
                return find_date(date)


def match_facts(sentence):
    """
    :param sentence: whole sentence string entered on the first iteration of the chatbot using the input function
    :return: undeclared experta facts
    """
    # load the spacy english dataset
    nlp = spacy.load('en_core_web_lg')
    # turn the whole sentence into lowercase, used for matching stations & the nlp tree result is often better this way
    # for this purpose
    doc = nlp(sentence.lower())
    # lemmatize sentence, and create a new subtree from it
    lemmatized_sentence = []
    for word in doc:
        lemmatized_sentence.append(word.lemma_)
    output_string = " ".join(lemmatized_sentence)
    # create new tree with lemmatized words, this is done to create a less congested tree
    # which is easier to extract information from
    doc = nlp(output_string)
    # creating return variables
    delay = None
    date_and_time_array_leave = []
    date_and_time_array_come_back = []
    depart_date = ""
    depart_time = ""
    return_date = ""
    return_time = ""
    returnYN = None
    departure_station = ""
    destination_station = ""
    # loop to find keywords, when keywords are found we use the subtrees from them to find key items such as dates and
    # confirmation of user wanting to book, to help fill out the KE. Base case is all the information in one sentence,
    # working downwards

    for words in doc:
        # looking for root words in tree that convey that the user wants to go somewhere, or book a train ticket and
        # following that subtree to find additional information
        for root_words in allowed_root_word_list:
            if root_words == words.lemma_:
                subtree_here = list(words.subtree)
                # if user specifies they want to go somewhere , look for additional information if it has not been
                # filled in yet
                for words in subtree_here:
                    # using prepositions we go deeper into the subtrees to locate relevant information
                    destination_station = get_root_words_to(words, destination_station)
                    departure_station = get_root_words_from(words, destination_station, departure_station)
                    if get_root_time(words) is not None:
                        date_and_time_array_leave.append(get_root_time(words))
        # # delay case
        # if words.lemma_.lower() == "delay":
        #     delay = True

        # looking for root words in tree that convey that the user wants to get a return ticket
        for root_words in return_list:
            if root_words == words.lemma_:
                # checking if user specifies no return, e.g no return , without return using .head which
                # gets to the root of the word return - therefore we can check the words predicating that word for
                # negatives
                return_subtree = list(words.head.subtree)
                for words in return_subtree:
                    for lang_words in negative_list:
                        if words.text == lang_words:
                            returnYN = False
                if returnYN == None:
                    returnYN = True
                # if user specifies a return , look for additional information if it has not been filled in yet
                return_ticket_subtree = list(words.subtree)
                for words in return_ticket_subtree:
                    destination_station = get_root_words_to(words, destination_station)
                    departure_station = get_root_words_from(words, destination_station, departure_station)
                    if get_date(words) is not None:
                        date_and_time_array_come_back.append(get_date(words))

                # if the return subtree does not contain date, look for a date higher up the tree.
                # this is sometimes the case for sentences like "be back on the 20th of december at 12:30"
                # only looks as far as return word, therefore is safe
                if len(date_and_time_array_come_back) == -1:
                    look_for_information_higher = list(words.head.subtree)
                    print(look_for_information_higher)
                    # checking if the word has a parent
                    if len(look_for_information_higher) > 0:
                        evaluate_subtree = list(look_for_information_higher[0].subtree)
                        print("here", evaluate_subtree)
                        for words in evaluate_subtree:
                            destination_station = get_root_words_to(words, destination_station)
                            departure_station = get_root_words_from(words, destination_station, departure_station)
                            if get_root_time(words) is not None:
                                date_and_time_array_leave.append(get_root_time(words))

    # sorting dates picked up
    dates_leave = []
    times_leave = []
    dates_come_back = []
    times_come_back = []
    unique_dates_leave = unique_list(date_and_time_array_leave)
    unique_dates_return = unique_list(date_and_time_array_come_back)
    for elements in unique_dates_leave:
        if len(elements) == 4:
            times_leave.append(elements)
        elif len(elements) == 6:
            dates_leave.append(elements)
    for elements2 in unique_dates_return:
        if len(elements2) == 4:
            times_come_back.append(elements2)
        elif len(elements2) == 6:
            dates_come_back.append(elements2)
    # check if dates found, return them
    if len(dates_leave) > 0:
        depart_date = dates_leave[0]
    if len(times_leave) > 0:
        depart_time = times_leave[0]
    if len(dates_come_back) > 0:
        return_date = dates_come_back[0]
    if len(times_come_back) > 0:
        return_time = times_come_back[0]

    # yield facts to engine if they are picked up
    if destination_station != "":
        yield DestinationTrainStation(destination_station)
    if departure_station != "":
        yield DepartTrainStation(departure_station)
    if depart_date != "":
        yield DepartDate(depart_date)
    if depart_time != "":
        yield DepartBeforeTime(depart_time)
    if return_time != "":
        yield ReturnTime(return_time)
    if return_date != "":
        yield ReturnDate(return_date)
    if returnYN is True:
        yield ReturnYN(returnYN)
    if returnYN is False:
        yield ReturnYN(returnYN)
    if delay is not None:
        yield Delay(True)


def find_time_scenario(sentence):
    """
    :param sentence: sentence from the input function called by the bot
    :return: date or time string, None if not found
    """
    nlp = spacy.load('en_core_web_lg')
    doc = nlp(sentence)
    time = ""
    if len(doc) == 1:
        time = find_date(doc)
    elif len(doc) < 4:
        time = find_date(doc)
    else:
        for words in doc:
            for root_words in prepositions_list_time_depart:
                if root_words == words.lemma_:
                    date = list(words.subtree)
                    if find_date(date) != None:
                        time = find_date(date)
    if time != "":
        return time


def return_yes_or_no(string):
    """
    :param string: sentence from the input function called by the bot
    :return: string containing yes or no, else None, this is used to confirm whether a return ticket is wanted
    """
    if string == "yes":
        return "yes"
    elif string == "no":
        return "no"


def find_station(sentence):
    """
    :param sentence:  sentence from the input function called by the bot
    :return: TLC of the station identified within the string, or an empty string if nothing is found
    """
    nlp = spacy.load('en_core_web_lg')
    doc = nlp(sentence.lower())
    departure_station = ""
    if len(doc) == 1:
        temp = []
        temp.append(doc)
        departure_station = match_train_stations(temp)
    else:
        for words in doc:
            for tree_words in where_from:
                if tree_words == words.lemma_:
                    if departure_station == "":
                        departure_station = list(words.subtree)
                        departure_station = match_train_stations(departure_station)
                    else:
                        pass
    if departure_station is "":
        departure_station = match_train_stations(doc)
    if departure_station is not "":
        return departure_station
