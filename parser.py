import os
import sys
import re

# need recursive decent parsing

def handle_line_continuation(source_code):
    # Utility functions for \ token which is used for line continuation in Translation Units
    # source_code is a list of lines
    # this function returns a list of lines with line continuations handled
    i = 0
    while i < len(source_code):
        line = source_code[i]
        if line.endswith('\\\n'):
            source_code[i] = line[:-2] + source_code[i+1]
            # Remove the backslash and newline, and concatenate with next line
            del source_code[i+1]  # Remove the next line as it has been merged
        else:
            i += 1  # Move to the next line only if no continuation was found

    return source_code


def c_preprocessor_include(compile_directory = None,
                           include_path=None, custom_include_paths=[]):

    # compile_directory is the directory where all source files are located
    # walk thorugh the compile_directory to collect all lines of
    # code from all source files, and handle line continuations
    # each .c file corresponds to a single python list of lines

    if include_path is None:
        print("No include path provided, using current directory as default include path.")
        include_path = os.getcwd()

    if compile_directory is None:
        print("No compile directory provided, " \
        "using current directory as default compile directory.")
        compile_directory = os.getcwd()

    custom_include_paths.append(include_path)
    # add default include path to custom include paths for searching header files

    source_code = []

    for root, dirs, files in os.walk(compile_directory):
        for file in files:
            if file.endswith('.c'):
                cfile = os.path.join(root, file)
                with open(cfile, 'r') as file:
                   lines = file.readlines()
                   lines = handle_line_continuation(lines)
                   source_code.append(lines)

    mainlines = []

    for cfile in source_code:
        mainlines = cfile
        includeGuard = []
        include_found = False
        include_index = 0
        while True:
            mainlines = handle_line_continuation(mainlines)
            for line in mainlines:
                if line.startswith('#include '):
                    include_index = mainlines.index(line)
                    line = line['#include '.__len__():] # remove #include
                    words = re.findall(r'[a-zA-Z0-9_-]+|\s|.|"|<|>',line)
                    words_ = []
                    for i in words:
                        if i == ' ' or i == '\t' or i == '\n':
                            continue
                        words_.append(i)
                    filename = ''
                    cfilename = ''
                    if len(words_) != 5:
                        print("Error : Invalid include syntax at line " + str(include_index+1))
                        print("Include syntax should be either #include <filename> or #include \"filename\"")
                        sys.exit(1)
                    if words_[0] == '<' and words_[4] != '>':
                        print("Error : Invalid include syntax at line " + str(include_index+1))
                        print("Include syntax should be either #include <filename> or #include \"filename\"")
                        sys.exit(1)

                    if words_[0] == '"' and words_[4] != '"':
                        print("Error : Invalid include syntax at line " + str(include_index+1))
                        print("Include syntax should be either #include <filename> or #include \"filename\"")
                        sys.exit(1)
                    for i in range(len(words_)):
                            if words_[i] == '"':
                                cfilename = words_[i+1] + words_[i+2] + words_[i+3]
                                break
                            if words_[i] == '<':
                                filename = words_[i+1] + words_[i+2] + words_[i+3]
                                break
                    if filename != '':
                        include_file = filename
                        include_found = True
                        if include_file in includeGuard:
                            mainlines[include_index] = ""
                            break
                        includeGuard.append(include_file)
                        # handle both forward slash and backslash for include paths
                        if '/' in include_file:
                            include_file = include_file.replace('/', '\\')
                        for ipath in custom_include_paths:
                            if os.path.exists(ipath + "\\" + include_file):
                                with open(ipath + "\\" + include_file , 'r') as inc_file:
                                    innerLines = inc_file.readlines()
                                    mainlines[include_index:include_index+1] = innerLines
                                break
                            else:
                                print(f"Error : File {include_file} not found in {ipath}")
                                sys.exit(1)
                    elif cfilename != '':
                        include_custom_file = cfilename
                        include_found = True
                        if include_custom_file in includeGuard:
                            mainlines[include_index] = ""
                            break
                        includeGuard.append(include_custom_file)
                        mypath = os.getcwd()
                        # handle both forward slash and backslash for include paths
                        if '/' in include_custom_file:
                            include_custom_file = include_custom_file.replace('/', '\\')
                        if os.path.exists(mypath + "\\" + include_custom_file):
                            with open(mypath + "\\" + include_custom_file , 'r') as inc_file:
                                innerLines = inc_file.readlines()
                                mainlines[include_index:include_index+1] = innerLines
                            break
                        else:
                            # report file not found in any custom path
                            print(f"Error : File {include_custom_file} not found in {mypath}")
                            sys.exit(1)

                else:
                    include_found = False

            if not include_found:
                break

    return source_code


def remove_comments(source_code):
    # source_code is a list of lists of lines,
    # each inner list corresponds to a source file
    # this function removes comments from the source code
    # and returns a list of lists of lines without comments
    for i in range(len(source_code)):
        lines = source_code[i]
        in_multiline_comment = False
        for j in range(len(lines)):
            line = lines[j]
            if in_multiline_comment:
                if '*/' in line:
                    in_multiline_comment = False
                    lines[j] = line.split('*/', 1)[1]  # Remove the comment part
                else:
                    lines[j] = ''  # Remove the entire line
            else:
                if '/*' in line:
                    in_multiline_comment = True
                    lines[j] = line.split('/*', 1)[0]  # Remove the comment part
                elif '//' in line:
                    lines[j] = line.split('//', 1)[0]  # Remove the comment part

    return source_code


# define macro machinary
def c_preprocessor_define(source_code):
    # source_code is a list of lists of lines, each inner list corresponds to a source file
    for cfile in source_code:
        for line in cfile:
            if line.startswith('#define '):
                parts = line.split()
                def_index = cfile.index(line)
                key = ""
                cfile[def_index] = "" #remove #define line

                if len(parts) >= 3:
                    key = parts[1]
                    value = ' '.join(parts[2:]) # join the rest as value

                    if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*(\(.*\))?$', key):
                        print(f"Error : Invalid macro name {key} at line {def_index+1}")
                        print("Macro names must start with a letter or underscore, followed by letters, digits, or underscores.")
                        print("For example: valid_macro_name or macroName123 or macro_name(param1, param2)")
                        sys.exit(1)
                    if '(' in key and ')' in key:
                        macro_name = key.split('(')[0]
                        parameters = key.split('(')[1].split(')')[0].split(',')

                        parameters = [param.strip() for param in parameters] # clean whitespace
                        for param in parameters:
                            if not param.isidentifier():
                                print(f"Error : Invalid parameter name {param} in macro {macro_name} at line {def_index+1}")
                                print("Macro parameter names must be valid identifiers.")
                                print("For example: param1, param_name, arg123")
                                sys.exit(1)
                        for i in range(def_index + 1, len(cfile)):
                            if cfile[i].startswith('#define '):
                                next_parts = cfile[i].split()
                                next_key = next_parts[1].split('(')[0]
                                if next_key == macro_name:
                                    break

                            if cfile[i].startswith('#undef '):
                                undef_parts = cfile[i].split()
                                undef_key = undef_parts[1]
                                if undef_key == macro_name:
                                    break

                            # check if macro name used in string literals
                            if '"' in cfile[i]:
                                string_literals = re.findall(r'"(.*?)"', cfile[i])
                                if any(macro_name in literal for literal in string_literals):
                                    continue  # Skip replacement in this line

                            if macro_name in cfile[i]:
                                # extract arguments
                                pattern = re.escape(macro_name) + r'\s*\((.*?)\)'
                                matches = re.finditer(pattern, cfile[i])
                                for match in matches:
                                    args_str = match.group(1)
                                    args = [arg.strip() for arg in args_str.split(',')]
                                    if len(args) != len(parameters):
                                        print(f"Error : Argument count mismatch for macro {macro_name} at line {i+1}")
                                        sys.exit(1)
                                    expanded_value = value
                                    for param, arg in zip(parameters, args):
                                        expanded_value = re.sub(r'\b' + re.escape(param) + r'\b', arg, expanded_value)
                                    cfile[i] = cfile[i].replace(match.group(0), expanded_value)

                    else:
                        for i in range(def_index + 1, len(cfile)):
                            if cfile[i].startswith('#define '):
                                next_parts = cfile[i].split()
                                next_key = next_parts[1]
                                if next_key == key:
                                    break

                            # handle undef processor directive
                            if cfile[i].startswith('#undef '):
                                undef_parts = cfile[i].split()
                                undef_key = undef_parts[1]
                                if undef_key == key:
                                    break

                            # check if macro name used in string literals
                            if '"' in cfile[i]:
                                string_literals = re.findall(r'"(.*?)"', cfile[i])
                                if any(key in literal for literal in string_literals):
                                    continue  # Skip replacement in this line

                            if key in cfile[i]:
                                cfile[i] = cfile[i].replace(key, value)


    return source_code

def c_preprocessor_conditional_expression_evaluator(expression,line_number):

    line_number = line_number + 1  # Adjust line number for user-friendly reporting

    # expression is a string
    # this function returns True or False based on the evaluation of the expression


    # lexical analysis - tokenize the expression
    invalid_operators = ('++','{', '}' , '$' , '@' ,'--', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '>>=', '<<=')

    for op in invalid_operators:
        if op in expression:
            return "Error : Invalid operator in expression - " + op

    stringList = re.findall(r'(!defined)\((\w+)\)\s*|(defined)\((\w+)\)\s*|(!defined)\s+(\w+)\s*|(\w+)|(&&|\|\||==|!=|\(|\)|\
                            &|\||!|<<|>>|<|>|>=|<=|\+|-|/|%|\*|)\s*', expression)

    # convert list of tuples to list of strings
    tokens = []

    for tup in stringList:
        for item in tup:
            if item != '':
                tokens.append(item)

    # syntax checking & parsing
    for i in range(len(tokens)):
        # check defined and !defined syntax
        if tokens[i] in ('defined','!defined'):
            if tokens[i+1].isidentifier() == False and tokens[i+1].isnumeric() == False:
                print("Error : Invalid expression syntax after defined or !defined, at line " + str(line_number))
                sys.exit(1)
        # check counts of opening and closing parentheses
        open_parens = tokens.count('(')
        close_parens = tokens.count(')')
        if open_parens != close_parens:
            print("Error : Mismatched parentheses in expression, at line " + str(line_number))
            sys.exit(1)
        # There must be a identifier or number before and after binary operators
        if tokens[i] in ('==', '!=', '<', '>', '<=', '>=', '+' , '*', '&' , '&&' , '||' , '|', '/', '%', '<<', '>>'):
            if i == 0 or i == len(tokens) - 1:
                print("Error : Invalid expression syntax - operator at start or end, at line " + str(line_number))
                sys.exit(1)
            if not (tokens[i-1].isidentifier() or tokens[i-1].isnumeric() or tokens[i-1] in ('(', ')','-', 'defined', '!defined', '!')):
                print("Error : Invalid expression syntax - operator before, at line " + str(line_number))
                sys.exit(1)
            if not (tokens[i+1].isidentifier() or tokens[i+1].isnumeric() or tokens[i+1] in ('(', ')', 'defined', '!defined', '-','!')):
                print("Error : Invalid expression syntax - operator after, at line " + str(line_number))
                sys.exit(1)
        if tokens[i] == '!':
            if i == len(tokens) - 1:
                print("Error : Invalid expression syntax - ! operator at end, at line " + str(line_number))
                sys.exit(1)
            if not (tokens[i+1].isidentifier() or tokens[i+1].isnumeric() or tokens[i+1] in ('(', 'defined', '!defined')):
                print("Error : Invalid expression syntax - ! operator before, at line " + str(line_number))
                sys.exit(1)
        if tokens[i] == '-':
            if i < len(tokens) - 1:
                if not (tokens[i+1].isidentifier() or tokens[i+1].isnumeric() or tokens[i+1] in ('(', 'defined', '!defined')):
                    print("Error : Invalid expression syntax - - operator before, at line " + str(line_number))
                    sys.exit(1)

        if tokens[i] not in ('defined','!defined'):
            if (tokens[i].isidentifier() or tokens[i].isnumeric()) and i < len(tokens) - 1:
                if(tokens[i+1].isidentifier() or tokens[i+1].isnumeric()) :
                    print("Error : Invalid expression syntax - missing operator between identifiers or numbers, at line " + str(line_number))
                    sys.exit(1)

    #Precedence dictionary
    precedence = {
    '!': 4 , 'defined': 4 , '!defined': 4, '*': 3, '/': 3, '%': 3, '+': 2, '-': 2, '<<': 1, '>>': 1,
    '<': 0, '>': 0, '<=': 0, '>=': 0, '==': -1, '!=': -1, '&&': -2, '||': -3 , '&': -4 , '|': -5,
    '(': -6 , ')': -6

    }

    output = []
    stack = []

    #build postfix expression
    for token in tokens:
        if (token.isidentifier() or token.isnumeric()) and token not in ('defined','!defined'):
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # Pop the '(' from the stack
        elif token in precedence:
            while (stack and stack[-1] != '(' and
                   precedence[stack[-1]] >= precedence[token]):
                output.append(stack.pop())
            stack.append(token)
    while stack:
        output.append(stack.pop())

    # evaluate postfix expression
    eval_stack = []
    for token in output:
        #Add guard for defined identifiers as 0
        if token.isnumeric():
            # handle zero
            if token == '0':
                eval_stack.append(None)
            else:
                eval_stack.append(int(token))
        elif token.isidentifier() and token not in ('defined','!defined'):
            eval_stack.append(0)  # Undefined identifiers are treated as 0
        elif token == '+':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(a + b)
        elif token == '-':
            #push only negative of the number
            a = eval_stack.pop()
            if a is None:
                a = 0
            eval_stack.append(-a)
        elif token == '*':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(a * b)
        elif token == '/':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(a // b)
        elif token == '%':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(a % b)
        elif token == '<<':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(a << b)
        elif token == '>>':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(a >> b)
        elif token == '<':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(int(a < b))
        elif  token == '==':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(int(a == b))
        elif token == '!=':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(int(a != b))
        elif token == '!defined':
            a = eval_stack.pop()
            if a is None:
                eval_stack.append(0)
            else:
                eval_stack.append(int(a == 0))
        elif token == 'defined':
            a = eval_stack.pop()
            if a is None:
                eval_stack.append(1)
            else:
              eval_stack.append(int(a != 0))
        elif token == '>':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(int(a > b))
        elif token == '<=':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(int(a <= b))
        elif token == '>=':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(int(a >= b))
        elif token == '&&':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(int(a and b))
        elif token == '||':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(int(a or b))
        elif token == '&':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(a & b)
        elif token == '|':
            b = eval_stack.pop()
            a = eval_stack.pop()
            if a is None:
                a = 0
            if b is None:
                b = 0
            eval_stack.append(a | b)
        elif token == '!':
            a = eval_stack.pop()
            if a is None:
                a = 1
            eval_stack.append(int(not a))

    result = eval_stack.pop()
    output = True if result is None else result

    #handle 0 case, octal, binary, hexadecimal numbers
    return bool(output)


def c_preprocessor_conditional_directive_evaluator(source_code):
    # source_code is a list of lines

    # Store line number and status of conditionals
    # Push to list when opening conditional found
    # Pop from list when closing conditional found
    # stack is list of lists (line_number, is_found_true_one_branch, result_of_condition)
    conditional_stack = []

    opening_conditionals = ('#if', '#ifdef', '#ifndef')
    other_conditionals = ('#elif', '#else','#endif','#elifdef','#elifndef')

    for line in source_code:
        # fetch the first word of the line
        line_number = source_code.index(line)
        first_word = line.split()[0] if line.split() else ''

        if first_word == '#if':
            condition = line[len(first_word):].strip()
            result = c_preprocessor_conditional_expression_evaluator(condition, line_number)
            #remove the line after processing
            source_code[line_number] = ""
            conditional_stack.append([line_number, 0 , result])  # (line_number, is_found_true_one_branch, result_of_condition)
        elif first_word == '#ifdef':
            condition = line[len(first_word):].strip()
            if condition.isidentifier() == False and condition.isnumeric() == False:
                print(f"Error : Invalid identifier in #ifdef at line {line_number+1}")
                sys.exit(1)
            result = c_preprocessor_conditional_expression_evaluator(condition, line_number)
            source_code[line_number] = ""
            conditional_stack.append([line_number, 0 , result])

        elif first_word == '#ifndef':
            condition = line[len(first_word):].strip()
            if condition.isidentifier() == False and condition.isnumeric() == False:
                print(f"Error : Invalid identifier in #ifndef at line {line_number+1}")
                sys.exit(1)
            result = c_preprocessor_conditional_expression_evaluator(condition, line_number)
            source_code[line_number] = ""
            conditional_stack.append([line_number, 0 , not result])


        elif first_word in other_conditionals:
            if not conditional_stack:
               print("Error : #" + first_word + " without matching #if at line " + str(line_number+1))
               sys.exit(1)

            condition = line[len(first_word):].strip()

            if first_word == '#elifdef':
                #convert to #elif defined()
                condition = "defined(" + condition + ")"
                first_word = '#elif'

            elif first_word == '#elifndef':
                #convert to #elif !defined()
                condition = "!defined(" + condition + ")"
                first_word = '#elif'

            if first_word == '#elif':
                result = c_preprocessor_conditional_expression_evaluator(condition, line_number)
                source_code[line_number] = ""
                TOS = conditional_stack[-1] # Top Of Stack
                if TOS[2] == False or TOS[1] == 1:
                    # make lines empty until now
                    for i in range(TOS[0]+1, line_number):
                        source_code[i] = ""
                if TOS[2] == True:
                    TOS[1] = 1

                TOS[2] = result
                TOS[0]  = line_number

            elif first_word == '#else':
                source_code[line_number] = ""
                if condition != "":
                    print("Error : #else should not have condition at line " + str(line_number+1))
                    sys.exit(1)
                TOS = conditional_stack[-1] # Top Of Stack
                if TOS[2] == False or TOS[1] == 1:
                    for i in range(TOS[0]+1, line_number):
                        source_code[i] = ""
                if TOS[2] == True:
                    TOS[1] = 1

                TOS[2] = not TOS[2]
                TOS[0]  = line_number


            elif first_word == '#endif':
                if condition != "":
                    print("Error : #endif should not have condition at line " + str(line_number+1))
                    sys.exit(1)
                source_code[line_number] = ""
                TOS = conditional_stack.pop()
                if TOS[2] == False or TOS[1] == 1:
                    for i in range(TOS[0]+1, line_number):
                        source_code[i] = ""


    # translations units are no more list of lines, but list of strings, each string is a translation unit
    translation_units = [''.join(cfile) for cfile in source_code]
    return translation_units



# 32 keywords in C89 / ANSI C
c89_ANSI_keywords = (
'auto' ,	'double' ,	'int' ,	'struct',
'break' ,	'else' ,	'long' ,	'switch'
'case' ,	'enum' ,	'register'	 ,  'typedef',
'char' ,	'extern'  ,	'return' ,	'union',
'const'	, 'float'	, 'short'	, 'unsigned',
'continue'	, 'for'	, 'signed'	, 'void',
'default'	, 'goto'	, 'sizeof'	, 'volatile',
'do'	, 'if'	, 'static'	, 'while'
)

# Inherited from C89 / ANSI C / added new 5 keywords in C99
c99_keywords = ( c89_ANSI_keywords + ('_Bool' , '_Complex' , '_Imaginary' , 'inline' , 'restrict') )

# Added new 7 keywords in C11
c11_keywords = ( c99_keywords + ('_Alignas' , '_Alignof' , '_Atomic' , '_Generic' , '_Noreturn' , '_Static_assert', '_Thread_local') )

c18_keywords = c11_keywords # No new keywords added in C18

# 16 new keywords added in  C23
c23_keywords = ( c18_keywords + ('constexpr' , 'nullptr' , 'typeof' , 'typeof_unqual' , '_BitInt','bool','true',

                 'false' , 'alignas' ,'auto' , 'alignof', 'static_assert', 'thread_local' , '_Decimal32', '_Decimal64', '_Decimal128') )

 

def c_types():
    # handle all typedef keywords in translation_units
    
    

def c_eval(expr,variable_array,structs):
    # expr is a list of tokens
    # machine code generated here
    
    binary_x64 = []
    
    eval_stack = []    
    for x in expr:
        if x.isidentifier() or x.isnumeric():
            eval_stack.append(x)    
        elif x == '->':
            a = expr.pop()
            b = expr.pop()            
        elif x == '.':
            a = expr.pop()
            b = expr.pop()
                


def c_tiger(translation_units):
    # translation_units is a list of strings each string is a translation unit
    # each translation unit is a C source file after preprocessing
    
    
    precedence_of_operators = {

    '*' : 3 , '+=' : 1 , '-=' : 1 , '*=' : 1 , '/=' : 1 , '%=' : 1 ,
    '>>=' : 1 , '<<=' : 1 , '&=' : 1 , '^=' : 1 , '|=' : 1 ,
    '.' : 5  ,
    '+' : 2 , '-' : 2 , '/' : 3 , '%' : 3 ,
    '>>' : 2 , '<<' : 2 , '<' : 1 , '>' : 1 , '<=' : 1 , '>=' : 1 ,
    '==' : 0 , '!=' : 0 , '&' : -1 , '^' : -2 , '|' : -3 ,
    '&&' : -4 , '||' : -5 , '!' : 4 , '~' : 4 ,
    '++' : 4 , '--' : 4 , '->' : 5 , 
    
    }
    
    
    tokens = r'(\w+|\->|,|\.|\*|{|}|\[|\]|==|=|\+=|\-=|\
               \*=|/=|%=|>>=|<<=|&=|\^=|\|=|\(|\)|\+\+|\+|--| \
                |\-|\||\^|&&|&||\|\||:|\?|!=|<=|>=|<<|<|\>>|>|\/|%|;|!|~)'
    
    ctokens = re.compile(tokens)
    binary_array = [] 
    variable_array = []
    structs = []
    typedefs = []
    address = 0x1000  # example starting address, for data segment       
    for sourceCode in translation_units:
        tokens = re.findall(ctokens , sourceCode)
        tokens = [item for item in tokens if item != '']
        stack = []
        output = []
        # infix to postfix conversion
        for token in tokens:        
            if token == '(':
                stack.append(token)
                output.append('1exprs1')    
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()  # Pop the '(' from the stack              
                output.append('1expre1')
            elif token == ';':
                while stack:
                    output.append(stack.pop())
                output.append('1end1')  # End of expression
            elif token == ',':  
                while stack and stack[-1] != '(':
                    output.append(stack.pop())             
            elif token == '?' :
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                output.append('1if1')
            elif token == ':':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                output.append('1then1')
            elif token == '=':
                output.append('1equ1')
            elif token == '{':
                output.append('1blockstart1')
            elif token == '}':
                output.append('1blockend1')
            elif token in precedence_of_operators:               
                if token == '++':
                    # Determine if it's a prefix or postfix increment
                    if output and (output[-1].isidentifier() or output[-1].isnumeric()):
                        output.append('1postfixplus1')           
                        continue
                elif token == '--':
                    # Determine if it's a prefix or postfix decrement
                    if output and (output[-1].isidentifier() or output[-1].isnumeric()):
                        output.append('1postfixminus1')           
                        continue                        
                while (stack and stack[-1] != '(' and
                       precedence_of_operators[stack[-1]] >= precedence_of_operators[token]):
                    output.append(stack.pop())
                stack.append(token)      
            else:
                output.append(token)
        while stack:
            output.append(stack.pop())
            
        
        print(output)    

        offset = 0  # distance from rsp register
        scope = 0
        blocks = [scope]
        return    
        i = 0    
        while i != len(output):
            var = []
            expr = []                
            if output[i] in ('char','short','int','float','long','double'):
                var.append('')                    
                var.append(output[i])                               
                if output[i] == 'char':
                    var.append(1)
                elif output[i] == 'short':
                    var.append(2)
                elif output[i] in ('int','long','float'):
                    var.append(4)
                elif output[i] == 'double':
                    var.append(8)                       
                var.append(scope)
                var.append(offset if scope else address)
                variable_array.append(var)        
            elif output[i] == '*':
                t = variable_array[-1][1]
                variable_array[-1][1] = 'pointer to ' + t
                variable_array[-1][2] = 8                
            elif output[i] == '1blockstart1':
                scope += 1
                blocks.append(scope)        
            elif output[i] == '1blockend1':
                blocks.pop()
                scope -= 1                           
            elif output[i] == '1equ1':   
                i += 1
                while output[i] != '1end1':
                    expr.append(output[i])
                    i += 1                                           
            elif output[i] == '()':
                t = variable_array[-1][1]
                if t.startswith("pointer to"):
                    t = t.split("pointer to",1)[1]    
                    variable_array[-1][1] = 'pointer to function taking no parameter returning' + t
                else:
                    variable_array[-1][1] = 'function returning ' + t    
            
            elif output[i].isidentifier():
                variable_array[-1][0] = output[i]
                
            i += 1       
            
            
        variable_array.append("end_of_translation_unit")
        structs.append("end_of_translation_unit")
        typedefs.append("end_of_translation_unit")
    
    print(variable_array)    
    return binary_array


def c_link(binary_code):
    
    pe = [0x5a4d,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,
          0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,
          0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,0x0000,
          0x0000,0x0000,
            
          # e_lfanew pe header offset
          0x00000080, "zero_until_0x80"]

units = [""" 
    
    int * t;
    
"""]

c_tiger(units)
   
    
# source = c_preprocessor_include(r"C:\Users\dogu1\OneDrive\Documents\cc", r"C:\Users\dogu1\OneDrive\Documents\cc")

# remove_comments(source)

# c_preprocessor_define(source)

# print(source)

# print(''.join([['1'],['2']]))

