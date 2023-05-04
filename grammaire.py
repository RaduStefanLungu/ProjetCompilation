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
    txt: charactere+
    charactere: /[A-Za-z_0-9]/ | /</ | />/ | /:/ | /\// | /=/ | /"/ | /,/
    dumbo_bloc: "{{" expressions_list "}}"
    expressions_list: expression ";" expressions_list
        | expression ";"
    expression: "print" string_expression                                   -> f_print
        | "for" variable "in" string_list "do" expressions_list "endfor"
        | "for" variable "in" variable "do" expressions_list "endfor"
        | variable ":=" string_expression                                   -> f_assign_var
        | variable ":=" string_list                                         -> f_assign_var
        | variable ":=" numbers                                             -> f_assign_var
    string_expression: string
        | variable
        | string_expression "." string_expression
    string_list: "(" string_list_interior ")"                               -> str_list
    string_list_interior: string | string "," string_list_interior
    variable: ( /_/ | /[A-Za-z]/) /[A-Za-z_0-9]/*
    string: "'" charactere* "'"
    numbers: integer                                                        -> int
        | float1                                                            -> flt1
        | float2                                                            -> flt2
        | float3                                                            -> flt3
    float1: integer "." integer
    float2: integer "."
    float3: "." integer
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
#PRINTER = "template"

def run_instructions(t):
    if t.data == 'f_print':
        print(string_constructor_2(t.children[0].children[0].children))

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

            elif x.data == 'int':
                the_value = int_constructor(x.children)

            elif x.data == 'flt1':
                the_value = float1_constructor(x.children)

            elif x.data == 'flt2':
                the_value = float2_constructor(x.children)

            elif x.data == 'flt3':
                the_value = float3_constructor(x.children)

            elif x.data == 'str_list':
                the_value = str_list_constructor(x.children[0])

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

def integer_constructor(numbers):
    string = ""
    for number in numbers.children:
        string += number.value
    return string

def int_constructor(numbers):
    return int(integer_constructor(numbers[0]))

def float1_constructor(numbers):
    int1 = integer_constructor(numbers[0].children[0])
    int2 = integer_constructor(numbers[0].children[1])
    return(float(int1 + "." + int2))

def float2_constructor(numbers):
    int1 = integer_constructor(numbers[0].children[0])
    return(float(int1 + "."))

def float3_constructor(numbers):
    int1 = integer_constructor(numbers[0].children[0])
    return(float("." + int1))

def string_list_constructor(list_inter):
    #print(list_inter)
    string = ""
    #print(list_inter.children[0])
    string += string_constructor_2(list_inter.children[0].children)
    if len(list_inter.children) == 2:
        string += ", "
        string += string_list_constructor(list_inter.children[1])
    return(string)

def str_list_constructor(list_inter):
    return("(" + string_list_constructor(list_inter) + ")")

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
        print 'JINXED';
        _Jinx := 69;
        nbr1 := 42.05;
        nbr2 := 1312.;
        nb3 := .22;
        liste := ('un', 'deux', 'trois');
        }}
'''

if __name__ == '__main__':
    run(ana_gram_1)
    # main()