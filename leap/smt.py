from z3 import *

import era
import event
import expression
import symbolicword

def state_formula(q: era.State, nvars: int, pos: int,
                  state_vars: list) -> list:
    ''' return the conjunctive formula representing a state

    if the index of the state q is 3 (in binary: 011)
    and if there are at most 8 states (so that we require nvars = 3 bits),
    we want to return the following formula:
    
    NOT(q0_pos) AND q1_pos AND q2_pos

    '''
    binary_q = list(bin(q.index())[2:]) # binary representation of q.index()
    binary_q = ['0']*(nvars - len(binary_q)) + binary_q # add leading 0 to ensure the next assert
    assert len(binary_q) == nvars
    
    formula = [] # formula to be constructed
    for i in range(nvars):
        if binary_q[i] == '1':
            formula.append(state_vars[pos][i])
        elif binary_q[i] == '0':
            formula.append(Not(state_vars[pos][i]))
        else:
            raise ValueError('smt.py: unexpected value in binary_q')
    return And(formula)

def find_last_occurrence(word: symbolicword.SymWord, event: event.Event, id: int) -> int:
    for index in range(id-1, -1, -1):
        if word[index].event == event:
            return index

def build_guard_formula(g: expression.Expression, time_vars: list, pos: int, last_pos: int):
    if last_pos == None:
        return []
    formula = []

    if g.expr == 'True':
        return formula
    
    for each_conjunct in g.conjuncts():
        bound = each_conjunct.bound()
        op_str = each_conjunct.op_str()
        if op_str == 'lt':
            formula.append(time_vars[pos] - time_vars[last_pos] < bound)
        elif op_str == 'le':
            formula.append(time_vars[pos] - time_vars[last_pos] <= bound)
        elif op_str == 'ge':
            formula.append(time_vars[pos] - time_vars[last_pos] >= bound)
        elif op_str == 'gt':
            formula.append(time_vars[pos] - time_vars[last_pos] > bound)
        elif op_str == 'eq':
            formula.append(time_vars[pos] - time_vars[last_pos] == bound)
        else:
            raise TypeError('smt.py: unexpected operator found in guard')
    return formula

def f_constraint(g: expression.SimpleExpression, time_vars: list, pos: int, last_pos: int): 
    bound = g.bound()
    op_str = g.op_str()
    curr_time = time_vars[pos] # variable representing the time of current event
    if last_pos == None:
        prev_time = 0 # if the event has not happened before, it happened at 0
    else:
        prev_time = time_vars[last_pos] # last time the same event happened
    if op_str == 'lt':
        return curr_time - prev_time < bound
    elif op_str == 'le':
        return curr_time - prev_time <= bound
    elif op_str == 'ge':
        return curr_time - prev_time >= bound
    elif op_str == 'gt':
        return curr_time - prev_time > bound
    elif op_str == 'eq':
        return curr_time - prev_time == bound
    else:
        raise TypeError('smt.py: unexpected operator found in guard')
    
def build_guard(g: expression.Expression, pos: int, word: symbolicword.SymWord, time_vars: list):
    guard_formula = []
    for each_conjunct in g.conjuncts():
        event_present = each_conjunct.var()
        last_pos = find_last_occurrence(word, event_present, pos)
        guard_formula.append(f_constraint(each_conjunct, time_vars, pos, last_pos))
    if guard_formula:
        return [And(guard_formula)]
    return guard_formula

def f_guard(word: symbolicword.SymWord, pos: int, time_vars: list):
    '''build the modified timed constraint 
       for the constraints present in the 
       symbolic event word[pos]
    '''
    conjuncts = word[pos].guard.conjuncts()
    modified_conjuncts = []
    for each_conjunct in conjuncts:
        event_present = each_conjunct.var()
        last_pos = find_last_occurrence(word, event_present, pos)
        modified_conjuncts.append(f_constraint(each_conjunct, time_vars, pos, last_pos))
    return [And(modified_conjuncts)]

def build_formula_for_event(era: era.ERA, event: event.Event, 
                            negword: symbolicword.SymWord,
                            state_vars: list, 
                            time_vars: list, 
                            pos: int,
                            last_pos: int):
    formulae = []
    for src, tgt in era.transitions_on_event[event.name]:
        if (era.states[src].status == False or 
           era.states[tgt].status == False):
           continue
        src_tgt_formula = [] 
        src_tgt_formula.append(state_formula(era.states[src], len(bin(era.nstates)[2:]), pos, state_vars))
        src_tgt_formula.append(state_formula(era.states[tgt], len(bin(era.nstates)[2:]), pos + 1, state_vars))

        for each_transition in era.transitions[src][tgt]:
            if each_transition.event != event:
                continue
            g = each_transition.guard
            g_formula = build_guard(g, pos, negword, time_vars)
            formulae.append(And(src_tgt_formula + g_formula))
    return formulae

def f_word(negword: symbolicword.SymWord, time_vars: list):
    phi = []
    for id in range(negword.len):
        phi += build_guard(negword[id].guard, id, negword, time_vars)
    return phi

def f_final_states(era: era.ERA, nvars: int, state_vars: list, pos: int):
    phi = []
    for each_state in era.states:
        if each_state.accepting:
            phi.append(state_formula(each_state, nvars, pos, state_vars))
    return Or(phi)

def check(era: era.ERA, negword: symbolicword.SymWord):
    # quick check when negword is EPSILON
    if negword.is_epsilon:
        return era.states[0].accepting
    
    nvars = len(bin(era.nstates)[2:])
    phi = [] # formula to be constructed

    # variables to denote states
    state_vars = [[Bool(f'q{i}_{pos}') for i in range(nvars)]
                                       for pos in range(negword.len+1)]

    # Real variables for denoting time stamps
    time_vars = [Real(f't_{i}') for i in range(negword.len)]

    # all variables in time_vars should be >= 0
    phi.append(And([time_vars[i] >= 0 for i in range(len(time_vars))]))

    # all variables in time_vars should be in increasing order
    phi.append(And([time_vars[i] >= time_vars[i-1] for i in range(1,len(time_vars))]))

    # formula for initial state
    phi.append(state_formula(era.initialstate, nvars, 0, state_vars))

    # formulae for transitions
    for i in range(negword.len):
        last_occurrence = find_last_occurrence(negword, negword[i].event, i)
        formulae = build_formula_for_event(era, negword[i].event, negword, state_vars, time_vars, i, last_occurrence)
        if formulae: # formulae != []
            phi.append(Or(formulae))
    
    # formula for accepting states
    phi.append(f_final_states(era, nvars, state_vars, negword.len))

    # formula for word
    phi.append(And(f_word(negword, time_vars)))

    s = Solver()
    s.add(phi)
    if str(s.check()) == 'sat':
        return True
    return False

def is_empty(w: symbolicword.SymWord) -> bool:
    '''check if an expression is empty
    '''
    # Real variables for denoting time stamps
    time_vars = [Real(f't_{i}') for i in range(w.len)]

    phi = []

    # all variables in time_vars should be >= 0
    phi.append(And([time_vars[i] >= 0 for i in range(len(time_vars))]))

    # all variables in time_vars should be in increasing order
    phi.append(And([time_vars[i] >= time_vars[i-1] for i in range(1,len(time_vars))]))

    # formula for word
    phi.append(And(f_word(w, time_vars)))

    s = Solver()
    s.append(phi)
    return (str(s.check()) == 'unsat')
