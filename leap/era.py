import copy

import event
import expression
import utils

class State:
    ''' 
    class for defining states of an automaton

    attributes --
    name : name of the state
    init : a boolean variable indicating whether the state is the initial state
    accepting : a boolean variable indicating whether the state is an accepting state

    init and accepting are optional attributes
    if not provided, they are set to False by default
    '''
    def __init__(self, 
                 statename: str, 
                 index: int,
                 init: bool = False, 
                 accepting: bool = False) -> None:
        self.name = statename
        self.__index = index
        self.init = init
        self.accepting = accepting
        self.status = True

    def __str__(self):
        return self.name
    
    def copy(self, index):
        return State(self.name, index, True if self.init else False, True if self.accepting else False)

    def get_name(self):
        return self.name
    
    def is_init(self):
        '''
        return True  if this state is the initial state,
        return False otherwise
        '''
        return self.init

    def is_accepting(self):
        '''
        return True  if this state is an accepting state,
        return False otherwise
        '''
        return self.accepting
    
    def index(self):
        return self.__index

class Transition:
    ''' class for describing transitions of an ERA

    attributes --
    src : a state
    '''
    def __init__(self, src: State, tgt: State,
                 event: event.Event, g: expression.Expression) -> None:
        self.src = src
        self.tgt = tgt
        self.guard = g
        self.event = event

    def __str__(self):
        return f'{self.src.name}:{self.tgt.name}:{self.event}:{self.guard}'

class ERA:
    '''
    an object of this class is an event recording automaton

    n : number of states
    m : number of events

    '''
    def __init__(self, n) -> None:
        self.nstates = n
        self.events = []
        
        self.states = []
        self.transitions = [[] for i in range(self.nstates)]
        for i in range(n):
            self.states.append(State('q' + str(i), i))
            self.transitions[i] = [[] for i in range(self.nstates)]
        
        self.initialstate = self.states[0]
        self.states[0].init = True
        self.transitions_on_event = {}

    def __str__(self) -> str:
        output_str = f'number of states: {self.states_count()}\n'
        for state_i in self.states:
            for state_j in self.states:
                for each_transition in self.transitions[state_i.index()][state_j.index()]:
                    output_str += f'edge:{each_transition} \n'
        for state in self.states:
            if state.accepting:
                output_str += f'{state} accepting  '
        return output_str

    def states_count(self) -> int:
        ''' return the number of states present in an ERA

        NOTE: era.nstates does not represent this number
        '''
        num = 0
        for q in self.states:
            if q.status == True:
                num += 1
        return num

    def add_state(self) -> State:
        index_of_new_state = self.nstates
        old_nstates = self.nstates
        self.nstates += 1
        
        # add a new state and add it to the era
        new_state = State('q' + str(index_of_new_state), 
                                 index_of_new_state)
        self.states.append(new_state)
        
        # add transitions
        # step 1: no incoming transitions to the new state
        for each in range(old_nstates):
            self.transitions[each].append([])
        # step 2: no outgoing transitions from the new state
        self.transitions.append([[] for i in range(self.nstates)])
        
        return new_state

    def out_transitions(self, src: State):
        return self.transitions[src.index()]
    
    def has_transition(self, src: State, event: event.Event, guard: expression.Expression, tgt: State) -> bool:
        if guard.expr == 'True':
            for each_transition in self.transitions[src.index()][tgt.index()]:
                self.del_transition(each_transition)
            return False
        
        for each_transition in self.transitions[src.index()][tgt.index()]:
            if each_transition.event == event:
                if (each_transition.guard.expr == 'True' or 
                   each_transition.guard == guard):
                    return True
        return False

    def add_transition(self, src:State, event: event.Event, guard: expression.Expression, tgt: State) -> None:
        # if the guard is True, then we only keep this transition between
        # src and tgt on the letter event
        to_be_deleted = []
        for t in self.transitions[src.index()][tgt.index()]:
            if t.event == event:
                if (utils.is_contained(guard, t.guard) or
                    t.guard.expr == 'True'):
                    return
                elif (utils.is_contained(t.guard, guard) or
                    guard.expr == 'True'):
                    to_be_deleted.append(t)
        for each in to_be_deleted:
            self.del_transition(each)
        self.nd_add_transition(src, tgt, event, guard)

    def exists_transition(self, src: State, event: event.Event, guard: expression.Expression) -> State:
        for each_state in range(self.nstates):
            for each_transition in self.out_transitions(src)[each_state]: 
                event_on_transition = each_transition.event
                guard_on_transition = each_transition.guard
                if event_on_transition == event and guard_on_transition == guard:
                    return each_transition.tgt
        return None
    
    def nd_add_transition(self, src: State, tgt: State, 
                          eventname: event.Event, 
                          guard: expression.Expression) -> None:
        self.transitions[src.index()][tgt.index()].append(Transition(src, tgt, eventname, guard))
        self.transitions_on_event.setdefault(eventname.name, []).append((src.index(), tgt.index()))

    def del_transition(self, transition: Transition) -> None:
        src_index = transition.src.index()
        tgt_index = transition.tgt.index()
        self.transitions[src_index][tgt_index].remove(transition)
        self.transitions_on_event[transition.event.name].remove((src_index, tgt_index))

    def del_state(self, state: State) -> None:
        state.status = False
        
        if state.accepting == True: 
            state.accepting = False

        # no outgoing transitions from state
        self.transitions[state.index()] = [[] for i in range(self.nstates)]

    def copy(self):
        copied_era = ERA(self.nstates)
        copied_era.events = [event for event in self.events]
        copied_era.states = []
        for i in range(self.nstates):
            copied_era.states.append(self.states[i].copy(i))
        copied_era.initialstate = copied_era.states[0]
        copied_era.transitions = [[[] for i in range(copied_era.nstates)] for j in range(copied_era.nstates)]
        for src in range(copied_era.nstates):
            for tgt in range(copied_era.nstates):
                copied_era.transitions[src][tgt] = [t for t in self.transitions[src][tgt]]
        copied_era.transitions_on_event = {}
        for i in self.transitions_on_event.keys():
            copied_era.transitions_on_event[i] = [t for t in self.transitions_on_event[i]]
        return copied_era