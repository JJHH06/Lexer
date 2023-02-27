# Created by: José Hurtarte
# Created on: 24/02/2023
# Last modified on: 26/02/2023
# Description: Automata module and class

from graphviz import Digraph

class Tree:
    def __init__(self, root):
        self.key = root
        self.leftChild = None
        self.rightChild = None

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
