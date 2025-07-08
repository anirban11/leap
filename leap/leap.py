import era
import symbolicword
import smt

import copy

def merge(pta: era.ERA, indexof_q_r: int, indexof_q_b: int):
    q_r = pta.states[indexof_q_r]
    q_b = pta.states[indexof_q_b]

    for each_state in range(pta.nstates): 
        for each_edge in pta.transitions[each_state][q_b.index()]: #incoming edge to q_b
            pta.del_transition(each_edge)   #delete the incoming edge
            pta.add_transition(pta.states[each_state],
                               each_edge.event,
                               each_edge.guard,
                               q_r)
    
    if q_b.accepting:
        q_r.accepting = True
    for tgt_state_index in range(pta.nstates):
        to_be_deleted = [] # collect all outgoing transitions from q_b
        for trans_q_b in pta.transitions[q_b.index()][tgt_state_index]: # iterating over every outgoing edge of q_b
            q_t = pta.states[tgt_state_index]
            e = trans_q_b.event
            g = trans_q_b.guard
            
            to_be_deleted.append(trans_q_b)
            pta.nd_add_transition(q_r, q_t, e, g) #adding transition from q_r
        for each in to_be_deleted:
            pta.del_transition(each) # deleting transition from q_b
    pta.del_state(q_b)
    

def intersects(pta: era.ERA, sminus: list[symbolicword.SymWord]):
    for each_word in sminus:
        if smt.check(pta, each_word):
            return True
    return False

def mark_all_successors_blue(pta: era.ERA, q: era.State, blue: list[int]):
    for each_state in range(pta.nstates):
        if len(pta.transitions[q.index()][each_state]) != 0:
            blue.append(each_state)
    return blue

def mark_all_reds_successors_blue(pta: era.ERA,  
                                  red: list[int], 
                                  blue: list[int]):
    for each_red_state in red:
        for each_state in range(pta.nstates):
            if len(pta.transitions[each_red_state][each_state]) != 0:
                if each_state not in red and each_state not in blue:
                    blue.append(each_state)
    return blue

def leap(pta: era.ERA, sminus: list[symbolicword.SymWord]):
    red, blue = [], []

    q_r = pta.initialstate
    
    # Original RPNI
    red.append(q_r.index())
    blue = mark_all_successors_blue(pta, q_r, blue)
    
    while len(blue) != 0:
        q_b = pta.states[blue.pop(0)]
        if q_b.status == False:
            continue
        for qr in red:
            q_r = pta.states[qr]
            temp_pta = copy.deepcopy(pta)
            merge(temp_pta, q_r.index(), q_b.index())
            if intersects(temp_pta, sminus) == False:
                pta = temp_pta 
                blue = mark_all_reds_successors_blue(pta, red, blue)
                # print(f'\nmerge SUCCEEDED between red:{q_r} and blue:{q_b}!!!')
                break
            # print(f'\nmerge FAILED between red:{q_r} and blue:{q_b}!!!')
        else:
            blue = mark_all_successors_blue(pta, q_b, blue)
            red.append(q_b.index())
    
    print(f'*** FINAL ERA ***\n {pta}')
