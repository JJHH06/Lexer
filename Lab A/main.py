import sys
from graphviz import Digraph

class Tree:
    def __init__(self, root):
        self.key = root
        self.leftChild = None
        self.rightChild = None

# cleans the input from whitespaces
# TODO: Modify to do this but with classes?
def clean_input(user_input):
    user_input = user_input.replace(' ','')
    
    return user_input

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



# Main function
def main():
    # this inputs the user input from the command line
    #print(sys.argv[1])
    user_input = '(a*|b*)aab' # dummy input
    user_input = clean_input(user_input) 
    #TODO: check if the input is valid
    user_input = format_input(user_input)
    print('Concats added: ',user_input)
    output = shunting_yard(user_input)
    print('Output: ',output)
    tree = build_tree(output)
    print('Tree Root: ',tree.key)
    digraph = Digraph(graph_attr={'dpi': str(200)})
    postorder_traversal_draw(tree, digraph)
    # instead of a pdf file, generate a png file with -Tpng:gd
    digraph.render('expression tree', format='png')
    




if __name__ == "__main__":
    main()
