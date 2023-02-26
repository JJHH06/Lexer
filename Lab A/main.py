import sys
from graphviz import Digraph
import copy
import re

class Tree:
    def __init__(self, root):
        self.key = root
        self.leftChild = None
        self.rightChild = None

class Automata:
    def __init__(self, states, alphabet, transitions, initial_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
    

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
    states = [x for x in right_automata.states if x not in right_automata.final_states] + left_automata.states
    initial_state = left_automata.initial_state
    final_states = left_automata.final_states
    alphabet = left_automata.alphabet.union(right_automata.alphabet)
    transitions = left_automata.transitions + right_automata.transitions

    for i in range(len(transitions)):
        if transitions[i][1] in left_automata.final_states:
            transitions[i] = ((transitions[i][0][0], transitions[i][0][1]), right_automata.initial_state)
        elif transitions[i][1] in right_automata.final_states:
            transitions[i] = ((transitions[i][0][0], transitions[i][0][1]), left_automata.final_states[0])
    
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
    state_offset = len(automata.states)
    automata_copy.states = [state + state_offset for state in automata_copy.states]
    automata_copy.initial_state += state_offset
    automata_copy.final_states = [state + state_offset for state in automata_copy.final_states]
    automata_copy.transitions = [((transition[0][0] + state_offset, transition[0][1]), transition[1] + state_offset) for transition in automata_copy.transitions]
    return automata_copy, state_offset

def positive_closure_automata(automata, current_state):
    automata_copy, state_offset = automata_state_change(automata)
    return concatenation_automata(kleene_automata(automata_copy, current_state+state_offset), automata), state_offset+1

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
        elif token == '|':
            stack.append(or_automata(stack.pop(), stack.pop(), next_state))
            next_state += 2
        elif token == '.':
            stack.append(concatenation_automata(stack.pop(), stack.pop()))
            next_state -= 1
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


#builds a tree based on the Tree class
# TODO: Modify to do this but with classes?
def build_tree(postfix_expression):
    unary_operators = ['*','+','?']
    binary_operators = ['|','.']
    stack = []
    for token in postfix_expression:
        # Checks if token is a valid operand
        if token not in unary_operators and token not in binary_operators:
            stack.append(Tree(token))
        # checks if token is a valid binary operator
        elif token in binary_operators:
            operator_tree = Tree(token)
            operator_tree.rightChild = stack.pop()
            operator_tree.leftChild = stack.pop()
            stack.append(operator_tree)
        # checks if token is a valid unary operator
        elif token in unary_operators:
            operator_tree = Tree(token)
            operator_tree.leftChild = stack.pop()
            stack.append(operator_tree)
    return stack.pop()


# cleans the input from whitespaces
# TODO: Modify to do this but with classes?
def clean_input(user_input):
    user_input = user_input.replace(' ','')
    
    return user_input

def postorder_traversal_draw(tree, digraph):
    if tree:
        if tree.leftChild:
            digraph.edge(str(id(tree)), str(id(tree.leftChild)))
            postorder_traversal_draw(tree.leftChild, digraph)
        if tree.rightChild:
            digraph.edge(str(id(tree)), str(id(tree.rightChild)))
            postorder_traversal_draw(tree.rightChild, digraph)
        digraph.node(str(id(tree)), str(tree.key))
    else:
        return





# TODO: Modify to do this but with classes?
def format_input(user_input):
    symbols = ['|','*','+','?']
    result = str()
    for i in range(len(user_input)):
        if (i != 0):
            #fist case we check if the previous character is a token and current character is a opening parenthesis
            if (user_input[i-1] not in symbols and user_input[i-1] != '('  and user_input[i] == '('):
                result = result + '.' + user_input[i]
            #second case we check if the previous character is a * or + or ? and current character is a token
            elif (user_input[i-1] in symbols[1:] and user_input[i] not in symbols and user_input[i] != ')'):
                result = result + '.' + user_input[i]
            #third case we check if the previous character is a closing parenthesis and current character is a token
            elif (user_input[i-1] == ')' and user_input[i] not in symbols and user_input[i] != '(' and user_input[i] != ')'):
                result = result + '.' + user_input[i]
            #last check if previous character is not a symbol and not a parenthesis and current character is not a symbol and not a parenthesi
            elif (user_input[i-1] not in symbols and user_input[i-1] != '(' and user_input[i-1] != ')' and user_input[i] not in symbols and user_input[i] != '(' and user_input[i] != ')'):
                result = result + '.' + user_input[i]
            else:
                result= result + user_input[i]
        else:
            result = result + user_input[i]
    return result

# Shunting yard algorithm
# Based on the wikipedia pseudocode and from from the pseudocode from geeksforgeeks
def shunting_yard(user_input):
    precedence_table= {'|':1,'.':2,'*':3,'+':3,'?':3,'(':-1,')':-1}
    operators = ['|','*','+','?','.']
    output = []
    operator_stack = []
    for token in user_input:
        if token in operators:
            while (len(operator_stack)>0 and precedence_table[token] <= precedence_table[operator_stack[-1]]):
                output.append(operator_stack.pop())
            operator_stack.append(token)
        else:
            if token != '(' and token != ')':
                output.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while (len(operator_stack)>0 and operator_stack[-1] != '('):
                    output.append(operator_stack.pop())
                operator_stack.pop()
    while (len(operator_stack)>0):
        output.append(operator_stack.pop())
    return output


def validate_input(user_input):
    if (len(user_input) == 0):
        print ('Invalid input: Empty input')
        return False
    if ('.' in user_input):
        print ('Invalid input: . is a reserved character')
        return False
    two_ors_regex = re.search(r'\|\s*\|', user_input)
    if (two_ors_regex):
        print('Invalid input: Two or more consecutive |, error at position: {}'.format(two_ors_regex.start()))
        return False
    initial_symbol_regex = re.search(r'^\s*[*+?|.]', user_input)
    if (initial_symbol_regex):
        print('Invalid input: Symbols at start are not a valid operation, error at position: {}'.format(initial_symbol_regex.start()))
        return False
    final_symbol_regex = re.search(r'[\s]*[|.]$', user_input)
    if (final_symbol_regex):
        print('Invalid input: Symbol at end not valid, error at position: {}'.format(final_symbol_regex.start()))
        return False
    empty_parenthesis_regex = re.search(r'\(\s*\)', user_input)
    if (empty_parenthesis_regex):
        print('Invalid input: Empty parenthesis, error at position: {}'.format(empty_parenthesis_regex.start()))
        return False
    operator_open_parenthesis_regex = re.search(r'\(\s*[+*?|.]', user_input)
    if (operator_open_parenthesis_regex):
        print('Invalid input: Operators after open parenthesis are not a valid operation, error at position: {}'.format(operator_open_parenthesis_regex.start()))
        return False
    operator_closing_parenthesis_regex = re.search(r'[|.]\s*\)', user_input)
    if (operator_closing_parenthesis_regex):
        print('Invalid input: Second of operation misssing, error at position: {}'.format(operator_closing_parenthesis_regex.start()))
        return False
    
    parenthesis_count = 0
    for i in range(len(user_input)):
        if (user_input[i] == '('):
            parenthesis_count += 1
        elif (user_input[i] == ')'):
            parenthesis_count -= 1
        if (parenthesis_count < 0):
            print('Invalid input: Mismatched parenthesis, cannot close a parenthesis that was not opened, error at position: {}'.format(i))
            return False
    if (parenthesis_count != 0):
        #get the last ocurrence of a parenthesis
        print('Invalid input: Parenthesis mismatch error, close all parenthesis to fix it')
        return False
    return True


# Main function
def main():
    # this inputs the user input from the command line
    #print(sys.argv[1])
    
    user_input = sys.argv[1] if len(sys.argv) > 1 else input('Enter a regular expression: ')

    if validate_input(user_input) and (len(user_input) > 0):
        user_input = clean_input(user_input)
        user_input = format_input(user_input)
        output = shunting_yard(user_input)
        print('Postfix: ',''.join(output))
        tree = build_tree(output)

        digraph = Digraph(graph_attr={'dpi': str(200)})
        postorder_traversal_draw(tree, digraph)
        digraph.render('expression tree', format='png')
        automata = build_automata(output)
        draw_automata(automata)
        print('Success!, expression tree and NFA png files generated :)')

if __name__ == "__main__":
    main()
