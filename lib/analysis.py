import argparse
import ast
import json
import os
import subprocess


available_test_tools = ['pytest', 'unittest']


def main(source_dir, test_dir, testing_tool, output_dir, save_pre_analysis):
    test_results = analyze(source_dir, test_dir, testing_tool, output_dir, save_pre_analysis)
    return test_results


def analyze(source_dir, test_dir, testing_tool, output_dir, save_pre_analysis):   

    # 1. ASSERT THAT THE DIRECTORIES EXIST
    directory_check(source_dir, test_dir, output_dir)

    # 2. GATHER TEST FILES
    test_files = gather_test_files(test_dir)           # list

    # 3. GATHER TEST CASES
    test_cases = gather_test_cases(test_files, testing_tool)              # dictionary

    # 4. GATHER TEST RESULTS
    test_results = gather_test_results(test_cases, source_dir, testing_tool)    # dictionary

    # 5. WRITE PRE-ANALYSIS WHEN save_pre_analysis IS TRUE
    write_pre_analysis(test_results, output_dir, save_pre_analysis)
    
    # 6. RETURN TEST RESULTS
    return test_results


def directory_check(source_dir, test_dir, output_dir):
    # check if pathlib exists
    # assert source_dir.exists(), f"Directory '{source_dir}' not found."
    if not source_dir.exists():
        os.makedirs(source_dir)
    # assert test_dir.exists(), f"Directory '{test_dir}' not found."
    if not test_dir.exists():
        os.makedirs(test_dir)
    # assert output_dir.exists(), f"Directory '{output_dir}' not found."
    if not output_dir.exists():
        os.makedirs(output_dir)


def gather_test_files(root_dir):
    test_files = []
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if (file.startswith('test_') or file.startswith('pytest_')) and file.endswith('.py'):
                test_files.append(root + '/' + file)

    return test_files


def gather_test_cases(files, testing_tool):
    separator = '::' if testing_tool == 'pytest' else '.'  # '::' for pytest and '.' for unittest

    test_cases = {}

    for file in files:
        test_cases[file] = {'type': [], 'test functions': []}
    
    for file in files:
        with open(file, 'r') as f:
            code = "".join(f.readlines())
            tree = ast.parse(code)

            imported_modules = set()
            test_functions = []

            for node in tree.body:
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_modules.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    imported_modules.add(node.module)
                elif isinstance(node, ast.ClassDef):
                    class_name = node.name
                    for class_node in node.body:
                        if isinstance(class_node, ast.FunctionDef):
                            if class_node.name.startswith('test_'):
                                test_functions.append(class_name + separator + class_node.name)
                elif isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        test_functions.append(node.name)

            test_cases[file]['type'] = list(imported_modules.intersection(set(available_test_tools)))
            test_cases[file]['test functions'] = test_functions

    return test_cases


def gather_test_results(test_cases, source_dir, testing_tool):
    test_results = {}  
    test_id = 0
    

    for file, test_module in test_cases.items():
        # check wether the test module import the selected testing tool module
        if testing_tool not in test_module['type']:
            continue

        for test_function in test_module['test functions']:
            test_results[test_id] = {'test_file': file, 'type': test_module['type'], 'test function' : test_function, 'test result' : '', 'coverage' : {}}

            # run testing tool
            if testing_tool == 'pytest':
                cmd = ['python3', '-m', 'coverage', 'run', '--source=' + source_dir.__str__(), '-m', testing_tool, '-k', test_function,  '-q', '--no-header', '--no-summary', file]
            else:
                cmd = ['python3', '-m', 'coverage', 'run', '--source=' + source_dir.__str__(), '-m', testing_tool, '-k', test_function, file]
            
            print(' '.join(cmd))    # show progress
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            output = result.stdout + result.stderr

            if output[0] == '.':                                # test pass
                test_results[test_id]['test result'] = 'P'
            else:                                               # test fail
                test_results[test_id]['test result'] = 'F'

            cmd = ['python3', '-m', 'coverage', 'json']
            result = subprocess.run(cmd, capture_output=True, text=True)

            with open('coverage.json') as f:
                coverage_info = json.load(f)
                test_results[test_id]['coverage'] = coverage_info

            test_id += 1

    return test_results

def write_pre_analysis(test_results, output_dir, save_pre_analysis):
    if save_pre_analysis:
        json_file = output_dir / 'test_results.json'
        with open(json_file, 'w') as f:
            json.dump(test_results, f, indent=4)


if __name__ == '__main__':
    main()
