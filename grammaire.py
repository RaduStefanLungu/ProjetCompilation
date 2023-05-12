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
    txt: charactere+                                                        -> f_text
    charactere: /[A-Za-z_0-9]/ | /</ | />/ | /:/ | /\// | /=/ | /"/ | /,/ | /\./
    dumbo_bloc: "{{" expressions_list "}}"
    expressions_list: expression ";" expressions_list
        | expression ";"
    expression: "print" string_expression                                   -> f_print
        | for_block
        | if_block
        | variable ":=" string_expression                                   -> f_assign_var
        | variable ":=" string_list                                         -> f_assign_var
        | variable ":=" numbers                                             -> f_assign_var
        | variable ":=" operation                                           -> f_assign_var
        | variable ":=" boolean                                             -> f_assign_var
        | variable ":=" logic_operation                                     -> f_assign_var
        | variable ":=" comparison                                          -> f_assign_var
    for_block: "for" variable "in" string_list "do" expressions_list "endfor"     -> f_for
        | "for" variable "in" variable "do" expressions_list "endfor"             -> f_for
    if_block: "if" condition "do" expressions_list "endif"                        -> f_if
    string_expression: string
        | variable
        | string "." string_expression
        | variable "." string_expression
    string_list: "(" string_list_interior ")"
    string_list_interior: string | string "," string_list_interior
    variable: ( /_/ | /[a-z]/) /[A-Za-z_0-9]/*
    string: "'" charactere* "'"
    numbers: integer                                                        -> int
        | float1                                                            -> flt1
        | float2                                                            -> flt2
        | float3                                                            -> flt3
    float1: integer "." integer
    float2: integer "."
    float3: "." integer
    integer: /[0-9]/+
    boolean: /True/ | /False/
    operation: numbers operator numbers
        | variable operator numbers
        | numbers operator variable
        | variable operator variable
    operator: /\+/ | /-/ | /\*/ | /\//
    logic_operation: boolean logic_operator boolean
        | variable logic_operator boolean
        | boolean logic_operator variable
        | variable logic_operator variable
    logic_operator: /&/ | /\^/
    comparison: numbers comparison_operator numbers
        | variable comparison_operator numbers
        | numbers comparison_operator variable
        | variable comparison_operator variable
    comparison_operator: /</ | />/ | /=/ | /!=/
    condition: boolean
        | variable
        | logic_operation
        | comparison

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
        s = t.children[0]
        while len(s.children) == 2:
            st = s.children[0]
            if st.data == 'string':
                print(string_constructor_2(st.children))
            elif st.data == 'variable':
                print(variables.get(string_constructor_from_token(st.children)))
            s = s.children[1]
        st = s.children[0]
        if st.data == 'string':
            print(string_constructor_2(st.children))
        elif st.data == 'variable':
            print(variables.get(string_constructor_from_token(st.children)))

    elif t.data == 'f_assign_var':
        
        the_variable_0 = t.children[0]
        the_value_0 = t.children[1]

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

            elif x.data == 'string_list':
                the_value = []
                children = x.children[0].children
                if len(children) == 2 :
                    while len(children) == 2:
                        the_value.append(string_constructor_2(children[0].children))
                        children = children[1].children
                if len(children) == 1 :
                    the_value.append(string_constructor_2(children[0].children))
            elif x.data == 'operation':
                the_value = resolve_operation(x)
            elif x.data == 'boolean':
                the_value = boolean_value(x)
            elif x.data == 'logic_operation':
                the_value = resolve_logic_operation(x)
            elif x.data == 'comparison':
                the_value = compare(x)

        variables[the_variable] = the_value

    elif t.data == 'f_text':
        print(string_constructor_2(t.children))

    elif t.data == 'f_for':
        for_variable_name = string_constructor_from_token(t.children[0].children)
        type_of_list = t.children[1].data   # string_list_interior or variable
        in_list = []
        if type_of_list == 'string_list':
            children = t.children[1].children[0].children
            if len(children) == 2 :
                while len(children) == 2:
                    in_list.append(string_constructor_2(children[0].children))
                    children = children[1].children
            if len(children) == 1 :
                in_list.append(string_constructor_2(children[0].children))
        elif type_of_list == 'variable':
            liste = variables.get(string_constructor_from_token(t.children[1].children))
            for e in liste:
                in_list.append(e)
        
        save_variables ={}
        for k in variables.keys():
                save_variables[k] = variables[k]

        for i in in_list:
            variables[for_variable_name] = i
            for chil in t.children[2].children:
                if chil.data == 'expressions_list':
                    chil = chil.children[0]
                run_instructions(chil)
            cles =[]
            for k in variables.keys():
                cles.append(k)
            for k in cles:
                del variables[k]
            for k in save_variables.keys():
                variables[k] = save_variables[k]
    elif t.data == 'f_if':
        type_of_condition = t.children[0].children[0].data
        if type_of_condition == 'boolean':
            condition = boolean_value(t.children[0].children[0])
        elif type_of_condition == 'variable':
            condition = variables.get(string_constructor_from_token(t.children[0].children[0].children))
        elif type_of_condition == 'logic_operation':
            condition = resolve_logic_operation(t.children[0].children[0])
        elif type_of_condition == 'comparison':
            condition = compare(t.children[0].children[0])
        if condition:
            cur = t.children[1]
            while len(cur.children) == 2:
                run_instructions(cur.children[0])
                cur = cur.children[1]
            run_instructions(cur.children[0])


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

def resolve_operation(x):
    if x.children[0].data == 'int':
        number1 = int_constructor(x.children[0].children)
    elif x.children[0].data == 'flt1':
        number1 = float1_constructor(x.children[0].children)
    elif x.children[0].data == 'flt2':
        number1 = float2_constructor(x.children[0].children)
    elif x.children[0].data == 'flt3':
        number1 = float3_constructor(x.children[0].children)
    else:
        number1 = variables.get(string_constructor_from_token(x.children[0].children))
    if x.children[2].data == 'int':
        number2 = int_constructor(x.children[2].children)
    elif x.children[2].data == 'flt1':
        number2 = float1_constructor(x.children[2].children)
    elif x.children[2].data == 'flt2':
        number2 = float2_constructor(x.children[2].children)
    elif x.children[2].data == 'flt3':
        number2 = float3_constructor(x.children[2].children)
    else:
        number2 = variables.get(string_constructor_from_token(x.children[2].children))
    if x.children[1].children[0].value == '+':
        return number1 + number2
    elif x.children[1].children[0].value == '-':
        return number1 - number2
    elif x.children[1].children[0].value == '*':
        return number1 * number2
    else:
        return number1 / number2

def boolean_value(x):
    if x.children[0].value == 'True':
        return True
    else:
        return False

def resolve_logic_operation(x):
    if x.children[0].data == 'boolean':
        if x.children[0].children[0].value == 'True':
            cond1 = True
        else:
            cond1 = False
    else :
        cond1 = variables.get(string_constructor_from_token(x.children[0].children))
    if x.children[2].data == 'boolean':
        if x.children[2].children[0].value == 'True':
            cond2 = True
        else:
            cond2 = False
    else :
        cond2 = variables.get(string_constructor_from_token(x.children[2].children))
    if x.children[1].children[0].value == '&':
        return cond1 and cond2
    if x.children[1].children[0].value == '^':
        return cond1 or cond2
    
def compare(x):
    if x.children[0].data == 'int':
        number1 = int_constructor(x.children[0].children)
    elif x.children[0].data == 'flt1':
        number1 = float1_constructor(x.children[0].children)
    elif x.children[0].data == 'flt2':
        number1 = float2_constructor(x.children[0].children)
    elif x.children[0].data == 'flt3':
        number1 = float3_constructor(x.children[0].children)
    else:
        number1 = variables.get(string_constructor_from_token(x.children[0].children))
    if x.children[2].data == 'int':
        number2 = int_constructor(x.children[2].children)
    elif x.children[2].data == 'flt1':
        number2 = float1_constructor(x.children[2].children)
    elif x.children[2].data == 'flt2':
        number2 = float2_constructor(x.children[2].children)
    elif x.children[2].data == 'flt3':
        number2 = float3_constructor(x.children[2].children)
    else:
        number2 = variables.get(string_constructor_from_token(x.children[2].children))
    if x.children[1].children[0].value == '>':
        return number1 > number2
    elif x.children[1].children[0].value == '<':
        return number1 < number2
    elif x.children[1].children[0].value == '=':
        return number1 == number2
    else:
        return number1 != number2

def run(program):
    dumbo_tree = dumbo_parser.parse(program)
    #print(dumbo_tree)
    # dumbo_tree(program)

    run_tree(dumbo_tree.iter_subtrees_topdown())


def run_tree(tree):
    temp = -1
    for inst in tree:
        # print('\n')
        #print(inst)
        #print(inst.data)
        if inst.data == 'f_for':
            temp = calc_number_of_expression_list(inst.children[2])
        elif inst.data == 'f_if':
            temp = calc_number_of_expression_list(inst.children[1])
        
        if inst.data == 'f_print' or inst.data == 'f_assign_var':
            temp = temp - 1
            if temp < 0:
                run_instructions(inst)
        else :
            run_instructions(inst)
        #print(temp)
        
def calc_number_of_expression_list(expression_list):
    if len(expression_list.children) == 2 :
        return 1 + calc_number_of_expression_list(expression_list.children[1])
    else:
        return 1

sentence3 = '''
        {{
            nom := 'De Pril';
            prenom := 'Julie';
            cours := ('Math discretes');
            print nom . prenom . nom;
        }}
'''

sentence = '''
        {{
            nom := 'Brouette';
            prenom := 'Quentin';
            cours := ('Logique 1', 'Logique 2', 'Algebre 1', 'Math elem .');
        }}
            <html>
            <head><title>{{print nom . ' ' . prenom;}}</title></head>
            <body>
            <h1>{{print nom . ' ' . prenom;}}</h1>
            Cours : {{for c in cours do
            print c . ', ';
            endfor;}}
            </body>
            </html>
            '''
sentence4 = '''
        {{
            nom := 'De Pril';
            prenom := 'Julie';
            cours := ('Math discretes');
        }}
            <html>
            <head><title>{{print nom . ' ' . prenom;}}</title></head>
            <body>
            <h1>{{print nom . ' ' . prenom;}}</h1>
            Cours : {{for c in cours do
            print c . ', ';
            endfor;}}
            </body>
            </html>
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

ana_gram_1 = '''
        <bal>
        texte1
        {{
        nom := 'Marry';
        my_var := nom;
        print my_var;
        print 'JINXED';
        _Jinx := 69;
        nbr1 := 42.05;
        nbr2 := 1312.;
        nb3 := .22;
        liste := ('un', 'deux', 'trois');
        print liste;
        for num in liste
            do print num;
        endfor;
        for num in ('quatre', 'cinq', 'six')
            do print num;
        endfor;
        op1 := 1 + 2;
        print op1;
        op2 := op1 * 4.;
        print op2;
        op3 := 0.5 - op2;
        print op3;
        op4 := op2 / op1;
        print op4; 
        }}
        texte2
        </bal>
'''

ana_gram_2 = '''
        <bal>
        texte1
        {{
        for i in ('un', 'deux', 'trois')
        do
            print i;
            for j in ('quatre', 'cinq', 'six')
            do print j;
            endfor;
        endfor;
        }}
        texte2
        </bal>
'''

sentence5 = '''
            {{
            cond1 := False;
            cond2 := True;
            cond3 := cond1 & cond2;
            print cond3;
            cond4 := cond1 ^ cond2;
            print cond4;
            }}
'''
sentence6 = '''
            {{
            number1 := 5.9;
            number2 := 6.;
            cond1 := number1 != number2;
            print cond1;
            cond2 := number2 > .34;
            print cond2;
            cond3 := 10 < number1;
            print cond3;
            cond4 := 10 = 10.0;
            print cond4;
            }}
'''
sentence7 = '''
        {{
        if 1 = 1
        do print 'hello';
        endif;
        cond1 := True;
        cond2 := False;
        if cond1 ^ cond2
        do
            for i in ('un', 'deux', 'trois')
                do print i;
            endfor;
        endif;
        if cond1 & cond2
        do
            print 'perdu';
        endif;
        print 'fin';
        }}
'''
sentence8 = '''
{{nom := 'Jinx';
liste_photo := ('un', 'deux', 'trois');}}
<html>
<head><title>{{print nom;}}</title></head>
<body>
<h1>{{print nom;}}</h1>
{{
i := 0;
for nom in liste_photo do
if i > 0 do print ', '; endif;
print '<a href="' . nom . '"> ' . nom . '</a>';
i := i + 1;
endfor;
}}
<br/>
Il y a {{print i;}} dans l album {{print nom;}}.
</body>
</html>
'''

if __name__ == '__main__':
    run(ana_gram_2)