# Created by: José Hurtarte
# Created on: 25/02/2023
# Last modified on: 26/02/2023
# Description: Automata module and class


from graphviz import Digraph
import copy

class Automata:
    def __init__(self, states, alphabet, transitions, initial_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
    

def embellish_automata(automata):
    state_map = {prev_state: new_state for new_state, prev_state in enumerate(automata.states)}
    states = [state_map[state] for state in automata.states]
    initial_state = state_map[automata.initial_state]
    
    final_states = [state_map[state] for state in automata.final_states]
    initial_state_map = {initial_state: 0, 0: initial_state}
    final_state_map = {final_states[i-1]:len(states)-i for i in range(1, len(final_states)+1)}
    transitions = []
    for transition in automata.transitions:
        new_transition = ((state_map[transition[0][0]], transition[0][1]), state_map[transition[1]])
        if new_transition[0][0] in initial_state_map:
            new_transition = ((initial_state_map[new_transition[0][0]], new_transition[0][1]), new_transition[1])
        if new_transition[1] in initial_state_map:
            new_transition = (new_transition[0], initial_state_map[new_transition[1]])
        if new_transition[0][0] in final_state_map:
            new_transition = ((final_state_map[new_transition[0][0]], new_transition[0][1]), new_transition[1])
        if new_transition[1] in final_state_map:
            new_transition = (new_transition[0], final_state_map[new_transition[1]])
        transitions.append(new_transition)
    initial_state = initial_state_map[initial_state]
    return Automata(states, automata.alphabet, transitions, initial_state, final_states)

def draw_automata(automata):
    f = Digraph('finite_state_machine', format='png')
    f.attr(rankdir='LR')
    f.attr('node', shape='circle') #makes all nodes circles
    # inner_nodes is equal to all the nodes that are not the initial state or the final states
    inner_nodes = [state for state in automata.states if state not in automata.final_states and state != automata.initial_state]
    f.node('start_mark', shape='point', style='invis')
    f.node(str(automata.initial_state))
    f.edge('start_mark', str(automata.initial_state))
    for operand in automata.alphabet:
        next_states = [transition[1] for transition in automata.transitions if transition[0] == (automata.initial_state, operand)]
        for next_state in next_states:
            f.edge(str(automata.initial_state), str(next_state), label=operand)
    for state in inner_nodes:
        f.node(str(state))
        for operand in automata.alphabet:
            next_states = [transition[1] for transition in automata.transitions if transition[0] == (state, operand)]
            for next_state in next_states:
                f.edge(str(state), str(next_state), label=operand)
    for state in automata.final_states:
        f.node(str(state), shape='doublecircle')
    f.render('NFA', format='png')
    

def operand_automata(subexpression, current_state):
    states = [current_state, current_state+1]
    alphabet = {subexpression}
    initial_state = current_state
    final_states = [current_state+1]
    transitions = [((current_state, subexpression), current_state+1)]
    return Automata(states, alphabet, transitions, initial_state, final_states)

def or_automata(right_automata, left_automata, current_state):
    # union of the states of the two automata
    states = left_automata.states + right_automata.states
    states.extend([current_state, current_state+1])
    initial_state = current_state
    final_states = [current_state+1]
    # union of the alphabet of the two automata
    alphabet = left_automata.alphabet.union(right_automata.alphabet)
    alphabet.add('ε')
    # union of the transitions of the two automata
    transitions = left_automata.transitions + right_automata.transitions
    # add transitions to the new initial state
    transitions.append(((current_state, 'ε'), left_automata.initial_state))
    transitions.append(((current_state, 'ε'), right_automata.initial_state))
    # add transitions from the final states of the two automata to the new final state
    for state in left_automata.final_states:
        transitions.append(((state, 'ε'), current_state+1))
    for state in right_automata.final_states:
        transitions.append(((state, 'ε'), current_state+1))
    return Automata(states, alphabet, transitions, initial_state, final_states)

def concatenation_automata(right_automata, left_automata):
    # union of the states of the two automata
    states = [x for x in left_automata.states if x not in left_automata.final_states] + right_automata.states

    initial_state = left_automata.initial_state
    final_states = right_automata.final_states
    alphabet = left_automata.alphabet.union(right_automata.alphabet)
    transitions = left_automata.transitions + right_automata.transitions

    for i in range(len(transitions)):
        if transitions[i][1] in left_automata.final_states:
            transitions[i] = ((transitions[i][0][0], transitions[i][0][1]), right_automata.initial_state)
    return Automata(states, alphabet, transitions, initial_state, final_states)

def kleene_automata(automata, current_state):
    states = automata.states
    states.extend([current_state, current_state+1])
    initial_state = current_state
    final_states = [current_state+1]
    alphabet = automata.alphabet
    alphabet.add('ε')
    transitions = automata.transitions
    # transition the final states of the automata to the initial state
    for state in automata.final_states:
        transitions.append(((state, 'ε'), automata.initial_state))
    # transition from the initial state to the initial state of the automata
    transitions.append(((current_state, 'ε'), automata.initial_state))
    # transition from the final states of the automata to the final state
    for state in automata.final_states:
        transitions.append(((state, 'ε'), current_state+1))
    # transition from the initial state to the final state
    transitions.append(((current_state, 'ε'), current_state+1))
    return Automata(states, alphabet, transitions, initial_state, final_states)

def question_automata(automata, current_state):
    epsilon_automata = operand_automata('ε', current_state)
    return or_automata(epsilon_automata, automata, current_state+2)

def automata_state_change(automata):
    automata_copy = copy.deepcopy(automata)
    state_offset = max(automata.states)+1
    automata_copy.states = [state + state_offset for state in automata_copy.states]
    automata_copy.initial_state += state_offset
    automata_copy.final_states = [state + state_offset for state in automata_copy.final_states]
    automata_copy.transitions = [((transition[0][0] + state_offset, transition[0][1]), transition[1] + state_offset) for transition in automata_copy.transitions]
    return automata_copy, state_offset

def positive_closure_automata(automata, current_state):
    automata_copy, state_offset = automata_state_change(automata)
    return concatenation_automata(kleene_automata(automata_copy, current_state+state_offset), automata), state_offset+2

def build_automata(postfix_expression):
    unary_operators = ['*','+','?']
    binary_operators = ['|','.']
    stack = []
    next_state = 0
    for token in postfix_expression:
        # Checks if token is a valid operand
        if token not in unary_operators and token not in binary_operators:
            stack.append(operand_automata(token, next_state))
            next_state += 2
        #else checks which operator is it
        elif token == '|':
            stack.append(or_automata(stack.pop(), stack.pop(), next_state))
            next_state += 2
        elif token == '.':
            stack.append(concatenation_automata(stack.pop(), stack.pop()))
        elif token == '*':
            stack.append(kleene_automata(stack.pop(), next_state))
            next_state += 2
        elif token == '?':
            stack.append(question_automata(stack.pop(), next_state))
            next_state += 4
        elif token == '+':
            plus_closure_element, state_offset = positive_closure_automata(stack.pop(), next_state)
            stack.append(plus_closure_element)
            next_state += state_offset
    return stack.pop()

