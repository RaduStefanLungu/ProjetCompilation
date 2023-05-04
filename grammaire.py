"""
Basic calculator
================
A simple example of a REPL calculator
This example shows how to write a basic calculator with variables.
"""
from lark import Lark, Transformer, v_args
import lark

try:
    input = raw_input   # For Python2 compatibility
except NameError:
    pass

# Data
#
# {{
# nom := ’ B r oue t te ’ ;
# prenom := ’ Quentin ’ ;
# c o u r s := ( ’ Logique 1 ’ , ’ Logique 2 ’ , ’ Al geb re 1 ’ , ’Math elem . ’ ) ;
# }}

# Template
# 
# <html>
# <head><t i t l e >{{ pr int nom. ’ ’ . prenom ; }}</ t i t l e ></head>
# <body>
# <h1>{{ pr int nom . ’ ’ . prenom ; }}</h1>
# Cours : {{ for c in c o u r s do
# pr int c . ’ , ’ ;
# e n d f o r ; }}
# </body>
# </html>

#TODO : completer la liste de tt les characteres

dumbo_grammar = """
    programme: txt
        | txt programme2
        | programme2
    programme2: dumbo_bloc | dumbo_bloc programme
    txt: charactere*
    charactere: /[A-Za-z_0-9]/ | /</ | />/ | /:/ | /\// | /=/ | /"/ | /,/
    dumbo_bloc: "{{" expressions_list "}}"
    expressions_list: expression ";" expressions_list
        | expression ";"
    expression: "print" string_expression                                   -> f_print
        | "for" variable "in" string_list "do" expressions_list "endfor"
        | "for" variable "in" variable "do" expressions_list "endfor"
        | variable ":=" string_expression                                   -> f_assign_var
        | variable ":=" string_list
        | variable ":=" numbers
    string_expression: string
        | variable
        | string_expression "." string_expression
    string_list: "(" string_list_interior ")"
    string_list_interior: string | string "," string_list_interior
    variable: ( /_/ | /[A-Za-z]/) /[A-Za-z_0-9]/*
    string: "'" charactere* "'"
    numbers: integer | float
    float: integer+ "." integer*
    integer: /[0-9]/+
    
    %import common.WS
    %ignore WS
"""


# class OptimusPrime(Transformer):
    
#     def __init__(self):
#         self.vars={}

#     def f_print(self,value):
#         print(value)
#         return value


# dumbo_parser = Lark(dumbo_grammar,parser='lalr',start='programme', ambiguity='explicit',transformer=OptimusPrime())
# dumbo = dumbo_parser.parse

dumbo_parser = Lark(dumbo_grammar,start='programme', ambiguity='explicit')
dumbo = dumbo_parser.parse

variables = {}
PRINTER = "template"

def run_instructions(t):

    if t.data == 'f_print':
        # print(string_constructor_2(t.iter_subtrees_topdown()))
        temp = string_constructor_2(t.children[0].children[0].children)
        if PRINTER != temp :
            PRINTER = temp
            print(PRINTER)
        # print(t.children)

    elif t.data == 'f_assign_var':
        
        the_variable_0 = t.children[0]
        the_value_0 = t.children[1]

        # Left here for debugging purposes.
        the_variable = None
        the_value = None

        for x in the_variable_0.iter_subtrees():
            if x.data == 'variable':
                the_variable = string_constructor_from_token(x.children)

        for x in the_value_0.iter_subtrees():
            if x.data == 'string':
                the_value = string_constructor_2(x.children)
        
            elif x.data == 'variable':
                the_value = variables.get(string_constructor_from_token(x.children))

        variables[the_variable] = the_value

def string_constructor_2(list):
    string = ""
    for tree in list:
        string += tree.children[0].value
    return string

def string_constructor_from_token(token_list):
    string = ""
    for token in token_list:
        string += token.value
    return string



def run(program):
    dumbo_tree = dumbo_parser.parse(program)
    # dumbo_tree(program)


    for inst in dumbo_tree.iter_subtrees_topdown():
        run_instructions(inst)
    print(variables)


sentence = '''<html>Case:{{
            _Axel := ('Baby','Shark') ;
            _Jinx := _Axel;
            i:= 0;
            for nom in _Axel do
                print '<a href="'.nom.'">'.nom.'</a>';
            endfor;

            }}</html>
            '''

sentence2 = '''
    <html>
        <head>
            <title> {{ print nom.' '.prenom;}} </title>
        </head>
        <body>
            <h1>
                {{ print nom.' '.prenom;}}
            </h1>
            Cours: {{ 
                for c in cours do
                    print c.', ';
                endfor;
                }}
        </body>
    </html>
'''

sentence3 = '''
        {{
            nom := 'De Pril';
            prenom := 'Julie';
            cours := ('Math discretes');
        }}

'''

ana_gram_1 = '''
        {{
        nom := 'Marry';
        my_var := nom;
        print 'JINXED' ;
        _Jinx := 69;
        }}
'''

if __name__ == '__main__':
    run(ana_gram_1)
    # main()