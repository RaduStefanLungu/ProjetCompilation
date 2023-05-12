#Le choix de Lark est arbitraire par rapport à Ply. Nous avions entendu dire qu'il était plus pratique d'utilisation.
#De plus cela nous permettait d'apprendre à utiliser une librairie de fonctions supplémentaire.
from lark import Lark

#Définition de tous les différents regex nécessaires pour l'analyse grammaticale.
#Ils correspondent bien à la grammaire décrite dans l'énoncé avec plusieurs regex ajoutés pour que
#la grammaire soit non-ambigue et soit plus pratique dans l'analyse syntaxique avec l'arbre créé par Lark.
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

#C'est le parser par défaut de Lark, les différents paramètres servent à dire que programme est l'axiome et qu'en cas d'ambiguité,
#tous les chemins possibles devraient être explorer. On aurait alors plusieurs output (en cas d'erreur).
dumbo_parser = Lark(dumbo_grammar,start='programme', ambiguity='explicit')
dumbo = dumbo_parser.parse

#Variables est le tableau de variable qui sera rempli au fur-et-à-mesure de l'exécution du compilateur.
#Le choix de la structure dictionnaire en Python est pratique
#car elle agit comme une table de hachage simplifiée dans son utilisation.
variables = {}

#String qui sera renvoyé en réponse à l'utilisateur.
#Il est rempli à chaque fois qu'une instruction est un texte ou est un print.
output = ""

#Fonction d'analyse syntaxique qui est appelée à chaque fois que le parser détecte un nouveau regex pour l'évaluer.
#En fonction du type de regex, il va suivre certaines instructions et appeler plusieurs fonctions afin de donner
#une réponse adéquate correspondant à l'instruction. Les variables globales variables et output sont remplies
#à chaque étape où cela est nécessaire ou demandé.
def run_instructions(t):
    global output
    if t.data == 'f_print':
        s = t.children[0]
        while len(s.children) == 2:
            st = s.children[0]
            if st.data == 'string':
                output += string_constructor_2(st.children)
            elif st.data == 'variable':
                output += variables.get(string_constructor_from_token(st.children))
            s = s.children[1]
        st = s.children[0]
        if st.data == 'string':
            output += string_constructor_2(st.children)
        elif st.data == 'variable':
            output += variables.get(string_constructor_from_token(st.children))

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
        output += string_constructor_2(t.children)

    elif t.data == 'f_for':
        for_variable_name = string_constructor_from_token(t.children[0].children)
        type_of_list = t.children[1].data
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

#Fonction qui renvoie un string qui correspond à la valeur de chaque charactère qui compose
#ce string rassemblées en une seule variable. Elle est utilisée pour toutes les chaines de caractère sauf les noms de variable
def string_constructor_2(list):
    string = ""
    for tree in list:
        string += tree.children[0].value
    return string

#Fonction similaire pour les noms de variables.
#Elle est nécessaire car les noms de variables ont leur propre grammaire qui est moins libre que celle des string.
def string_constructor_from_token(token_list):
    string = ""
    for token in token_list:
        string += token.value
    return string

#Fonction qui renvoie un string correspondant aux charactères lus qui forment le nombre entier.
def integer_constructor(numbers):
    string = ""
    for number in numbers.children:
        string += number.value
    return string

#Fonction qui renvoie un int transtypé à partir du string obtenu ci-dessus.
def int_constructor(numbers):
    return int(integer_constructor(numbers[0]))

#Fonction qui renvoie un float en partant du principe qu'un float est composé d'un int à gauche et d'un int à droite du point.
def float1_constructor(numbers):
    int1 = integer_constructor(numbers[0].children[0])
    int2 = integer_constructor(numbers[0].children[1])
    return(float(int1 + "." + int2))

#Les deux suivantes sont pour les cas où le float n'est composé que d'un int qui est soit à gauche, soit à droite du point.
def float2_constructor(numbers):
    int1 = integer_constructor(numbers[0].children[0])
    return(float(int1 + "."))

def float3_constructor(numbers):
    int1 = integer_constructor(numbers[0].children[0])
    return(float("." + int1))

#Fonction qui va renvoyer un int ou un float correspondant au résultat de l'opération demandée.
#Par défaut c'est un float qui sera renvoyé même si il existe une version entière, exemple : 4.5 / 1.5 = 3.0
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

#Renvoie un booléen correspondant à la valeur lue.
def boolean_value(x):
    if x.children[0].value == 'True':
        return True
    else:
        return False

#Résoud les opérations de logique or et and. Ne résoud pas les cas avec plus de deux termes comme a and b or c.
#Par soucis d'ambiguité, les opérations and et or s'écrivent & et ^.
#Fonction renvoyant le booléan correspondant au résultat.
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
    
#Fonction évaluant les comparaisons de deux nombres. Les nombres peuvent être entiers ou flottants car
#un transtypage automatique sera appliqué pour résoudre tout conflit. Par exemple : 42 = 42.0
#Fonction renvoyant le booléen correspondant au résultat.
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

#Fonction principale qui s'occupe de l'analyse grammaticale à l'aide d'un parser et des regex définis plus haut.
#Elle donne ensuite en paramètres l'arbres ainsi construit à la fonction suivante.
def run(program):
    dumbo_tree = dumbo_parser.parse(program)
    run_tree(dumbo_tree.iter_subtrees_topdown())

#Fonction qui va s'occuper de l'analyse syntaxique en passant chaque instruction qui correspond à un regex
#à la fonction run_instruction qui va effectuer la tâche qui y correspond.
#La variable temp sert à ne pas répetter deux fois chaque instruction dans un for ou dans un if.
#Ceci aurait probablement pu être éviter avec une meilleure analyse grammaticale.
def run_tree(tree):
    temp = -1
    for inst in tree:
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

#Fonction qui renvoie le nombre d'expression simple contenues dans l'expression_list d'un for ou d'un if.
def calc_number_of_expression_list(expression_list):
    if len(expression_list.children) == 2 :
        return 1 + calc_number_of_expression_list(expression_list.children[1])
    else:
        return 1

#Instructions appelées en premières qui se charge de l'input et de l'output fournis et donné à l'utilisateur.
#L'output sera rempli pendant l'analyse syntaxique.
if __name__ == '__main__':
    import sys
    variable = open(sys.argv[1]).read()
    structure = open(sys.argv[2]).read()
    programme = variable + structure
    run(programme)
    sys.stdout.write(output)