# Created by: José Hurtarte
# Created on: 20/02/2023
# Last modified on: 26/02/2023
# Description: Lexer for an infix regular expression

import sys
from graphviz import Digraph
import re

from Automata import *
from ExpressionTree import *

# cleans the input from whitespaces
# TODO: Modify to do this but with classes?
def clean_input(user_input):
    user_input = user_input.replace(' ','')
    
    return user_input

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
        print('Invalid input: Parenthesis mismatch error, close all parenthesis to fix it')
        return False
    return True


# Main function
def main():
    # receive inputs from command line or console input
    user_input = sys.argv[1] if len(sys.argv) > 1 else input('Enter a regular expression: ')
    # user_input = '0?(1?)?0*' #Dummy input, uncomment for debugging

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
        automata = embellish_automata(automata)
        draw_automata(automata)
        print('Success!, expression tree and NFA png files generated :)')

if __name__ == "__main__":
    main()
