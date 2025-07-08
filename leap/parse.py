import re

import symbolicword
import event

def extract_event_list(inp: str) -> event.EventList:
    event_names = inp.split(":")[-1]
    event_names = event_names.rstrip(' \n\t').split(',')
    event_list = event.EventList()
    for each in event_names:
        assert each != 'EPSILON'
        event_list.add_event(event.Event(each))
    return event_list

def parse_input(inp: str) -> tuple[list, list, list]:
    event_list = []
    list_of_pos_words = []
    list_of_neg_words = []

    clean_inp = ''.join(re.findall(r'\S', inp)) # remove whitespaces

    inp_list = clean_inp.split('[')
    event_list = extract_event_list(inp_list[0])

    for inp_words in inp_list[1:]:
        inp_word_list = inp_words[:-1].split(';')
        inp_word_type = inp_word_list[-1] # pos / neg

        list_of_symbolic_events = []
        for symbolic_event in inp_word_list[:-1]:
            list_of_symbolic_events.append(symbolicword.SymEvent(symbolic_event))
    
        if inp_word_type == 'pos':
            list_of_pos_words.append(symbolicword.SymWord(list_of_symbolic_events))
        elif inp_word_type == 'neg':
            list_of_neg_words.append(symbolicword.SymWord(list_of_symbolic_events))
        else:
            raise TypeError("unknown word type; allowed types are 'pos' and 'neg'")

    return (event_list, list_of_pos_words, list_of_neg_words)


    


