import ast
import os
import sys
import re
import json
import subprocess
import argparse

def print_ast(element:ast):
    print(ast.dump(element, indent=1))

def arg_parser():
    parser = argparse.ArgumentParser(description='Check if test case is valid')
    parser.add_argument('testcase', type=str, help='Test case file')
    return parser.parse_args()

def gather_testcase(testcase):
    # TODO fix path
    # path = '/root/bugsinpy/framework/bin/temp/spacy/spacy/tests'
    path = '../../chess/test'     
    #with open(testcase, 'r') as f:
    file_list = os.listdir(path)
    dir_list = []
    
    for file in file_list:
        # print(file)
        # Add subdirectories to file_list
        if os.path.isdir(path + '/' + file):
            dir_list.append(file)
            file_list.extend([file + '/' + f for f in os.listdir(path + '/' + file)])
        elif not file.endswith('.py'):
            dir_list.append(file)
        elif file.endswith('__init__.py'):
            dir_list.append(file)

    # sanitize first        
    for file in dir_list:
        print('dir: ' + file)
        file_list.remove(file)

    file_class_functions = {}
    for file in file_list:
        file_class_functions[file] = {'type': '', 'test_case': []}
    
    for file in file_list:
        class_name = ''
        all_functions = []
        # print(file)
        with open(path + '/' + file, 'r') as f:
            content = f.read()
            tree = ast.parse(content)
            # if file == 'test_chess2.py':
            #     print_ast(tree)
            # return
            for node in tree.body:
                # class name and function name
                if isinstance(node, ast.Import):
                    for n in node.names:
                        if n.name == 'pytest':
                            # print('pytest in ' + file)
                            file_class_functions[file]['type'] = 'pytest'
                        if n.name == 'unittest':
                            # print('unittest in ' + file)
                            file_class_functions[file]['type'] = 'unittest'
                
                if isinstance(node, ast.ImportFrom):
                    if node.module == 'pytest':
                        # print('pytest in ' + file)
                        file_class_functions[file]['type'] = 'pytest'
                    if node.module == 'unittest':
                        # print('unittest in ' + file)
                        file_class_functions[file]['type'] = 'unittest'

                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    for n in node.body:
                        if isinstance(n, ast.FunctionDef):
                            all_functions.append(class_name + '.' + n.name)

                # function name
                if isinstance(node, ast.FunctionDef):
                    all_functions.append(node.name)
                    # print()
        file_class_functions[file]['test_case'] = all_functions

    
    
    for file in file_list:
        print('file: ' + file)
        print('\ttypes: ')
        print('\t\t'+file_class_functions[file]['type'])
        print('\ttest cases: ')
        print('\t\t', file_class_functions[file]['test_case'])
        print()
    return file_list, file_class_functions

def check_testcase(testcase, file_list, file_class_functions):
    path = '../../chess/test'
    for file in file_list:
        cmd = 'python3 -m pytest --cov-report json --cov=thefuck tests/rules/test_pip_unknown_command.py::test_get_new_comman'
        for function in file_class_functions[file]:
            print(file, function)
            
    return True

def main():
    # args = arg_parser()
    file_list, file_class_fuctions = gather_testcase('args.testcase')
    # check_testcase('f', file_list, file_class_fuctions)

if __name__ == '__main__':
    main()