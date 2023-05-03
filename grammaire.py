"""
Basic calculator
================
A simple example of a REPL calculator
This example shows how to write a basic calculator with variables.
"""
from lark import Lark, Transformer, v_args


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
    expression: "print" string_expression
        | "for" variable "in" string_list "do" expressions_list "endfor"
        | "for" variable "in" variable "do" expressions_list "endfor"
        | variable ":=" string_expression
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


dumbo_parser = Lark(dumbo_grammar, start='programme', ambiguity='explicit')


dumbo = dumbo_parser.parse

def main():
    print("%s","HELLOW")

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
        _Jinx := 69;
        }}
'''


def test():
    print(dumbo_parser.parse(ana_gram_1).pretty())

if __name__ == '__main__':
    test()
    # main()