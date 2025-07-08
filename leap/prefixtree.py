import era
import symbolicword

def add_event_to_pta(pta: era.ERA, src_state: era.State, symbolic_event: symbolicword.SymEvent):
    eventname = symbolic_event.event
    guard = symbolic_event.guard

    if eventname.name == 'EPSILON':
        assert src_state == pta.initialstate
        pta.initialstate.accepting = True
        return src_state

    tgt_state = pta.exists_transition(src_state, eventname, guard)

    if tgt_state == None:        
        # add a new state 
        tgt_state = pta.add_state()

        # add the transition src -> tgt to pta
        pta.nd_add_transition(src_state, tgt_state, eventname, guard)
    
    # return tgt_state from where next transition is to be added
    return tgt_state

def add_word_to_pta(pta: era.ERA, word: symbolicword.SymWord) -> None:
    current_state = pta.initialstate
    for each_event in word:
        current_state = add_event_to_pta(pta, current_state, each_event)
    current_state.accepting = True


def create_prefix_tree(list_of_pos_words: list[symbolicword.SymWord]) -> era.ERA:
    prefix_tree = era.ERA(1) # initialize the pta with a single state
    for word in list_of_pos_words:
        add_word_to_pta(prefix_tree, word)
    return prefix_tree