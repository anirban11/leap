''' this file implements methods to convert 
    a sample consisting of guarded (aka zone) words 
    to an 'equivalent' sample consisting only 
    of simple (aka region) words
'''

from itertools import product

import expression
import symbolicword
import utils
import smt

def create_list_of_regions(m: int, events_list: list):
    ''' create a list of all the regions 
        
        arguments:

        m        = max constant
        n_clocks = number of clocks
    '''
    regions = []
    regions_per_clock = [[] for x in range(len(events_list))] 
    for j in range(len(events_list)): # for every clock
        x = str(events_list[j])
        for i in range(m):
            regions_per_clock[j].append(expression.SimpleExpression(f'{x}=={i}'))
            regions_per_clock[j].append(expression.ConjExpression(f'{x}>{i}&&{x}<{i+1}'))
        regions_per_clock[j].append(expression.SimpleExpression(f'{x}=={m}'))
        regions_per_clock[j].append(expression.SimpleExpression(f'{x}>{m}'))
    for region in product(*regions_per_clock):
        regions.append(expression.ConjExpression(region))
    return regions

def convert_to_region_words(w: symbolicword.SymWord, regions: list) -> list:
    new_word = [[] for s in range(len(w.symbolic_word))]
    
    for i, s in enumerate(w.symbolic_word):
        if s.event.name == 'EPSILON':
            # if EPSILON, we do not break it into regions
            new_word[i].append(s)
            continue
        z = s.guard # the zone present in the symbolic letter s
        for r in regions:
            if utils.intersects(z, r):
                new_word[i].append(symbolicword.SymEvent.constructUsingEventGuard(s.event, r))
    
    region_words = list(product(*new_word)) # every element here is a tuple
    region_words = list(map(list, region_words))
    list_of_region_words = []
    for each_rw in region_words:
        symword = symbolicword.SymWord(each_rw)
        if not smt.is_empty(symword):
            list_of_region_words.append(symword)
    return list_of_region_words

def convert_to_region_words_rpni(w: symbolicword.SymWord, regions: list, label) -> list:
    new_word = [[] for s in range(len(w.symbolic_word))]
    
    for i, s in enumerate(w.symbolic_word):
        if s.event.name == 'EPSILON':
            # if EPSILON, we do not break it into regions
            assert len(w.symbolic_word) == 1
            break
        z = s.guard # the zone present in the symbolic letter s
        for r in regions:
            if utils.intersects(z, r):
                new_word[i].append(symbolicword.SymEvent.constructUsingEventGuard(s.event, r))
    
    region_words = list(product(*new_word)) # every element here is a tuple
    region_words = list(map(list, region_words))
    list_of_region_words = []
    for each_rw in region_words:
        symword = symbolicword.SymWord(each_rw)
        if not smt.is_empty(symword):
            list_of_region_words.append(symword)
    region_words = list(map(tuple, list_of_region_words))
    new_region_words = [tuple(map(str, rw)) for rw in region_words]
    region_words = list(map(lambda rw: (tuple(rw), label), new_region_words))
    return region_words
