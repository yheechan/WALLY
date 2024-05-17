import argparse
import ast
import json
import os
import subprocess


available_test_tools = ['pytest', 'unittest']


class DirectoryNotFoundError(Exception):
    pass


def main():
    parser = analysis_parser()
    analyze(parser)


def analysis_parser():
    parser = argparse.ArgumentParser(description='Pre-analysis for MBFL')
    parser.add_argument('--source-dir', '-s', type=str, required=True,
                        help='Root directory of sources to be tested')
    parser.add_argument('--test-dir', '-t', type=str, required=True,
                        help='Root directory of test cases')
    parser.add_argument('--testing-tool', '-T', type=str, choices=available_test_tools, default='pytest', 
                        help='Testing tool to be used. Default is pytest')
    parser.add_argument('--output-dir', '-o', type=str, default='./pre-analysis/',
                        help='Directory of pre-analysis results will be stored')
    return parser


def analyze(parser):
    args = parser.parse_args()
    
    directory_check(args)

    test_files = gather_test_files(args.test_dir)           # list

    test_cases = gather_test_cases(test_files, args)              # dictionary

    test_results = gather_test_results(test_cases, args)    # dictionary

    with open(args.output_dir + "test_results.json", 'w') as f:
        json.dump(test_results, f, indent=4)

def directory_check(args):
    try:
        if not os.path.exists(args.source_dir):
            raise DirectoryNotFoundError(f"Directory '{args.source_dir}' not found.")
        if not os.path.exists(args.test_dir):
            raise DirectoryNotFoundError(f"Directory '{args.test_dir}' not found.")
        if not os.path.exists(args.output_dir):
            raise DirectoryNotFoundError(f"Directory '{args.output_dir}' not found.")
    except DirectoryNotFoundError as e:
        print("Error: ", e)


def gather_test_files(root_dir):
    test_files = []
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if (file.startswith('test_') or file.startswith('pytest_')) and file.endswith('.py'):
                test_files.append(root + '/' + file)

    return test_files


def gather_test_cases(files, args):
    separator = '::' if args.testing_tool == 'pytest' else '.'  # '::' for pytest and '.' for unittest

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


def gather_test_results(test_cases, args):
    test_results = {}  
    test_id = 0
    

    for file, test_module in test_cases.items():
        # check wether the test module import the selected testing tool module
        if args.testing_tool not in test_module['type']:
            continue

        for test_function in test_module['test functions']:
            test_results[test_id] = {'test_file': file, 'type': test_module['type'], 'test function' : test_function, 'test result' : '', 'coverage' : {}}

            # run testing tool
            if args.testing_tool == 'pytest':
                cmd = ['python3', '-m', 'coverage', 'run', '--source=' + args.source_dir, '-m', args.testing_tool, '-k', test_function,  '-q', '--no-header', '--no-summary', file]
            else:
                cmd = ['python3', '-m', 'coverage', 'run', '--source=' + args.source_dir, '-m', args.testing_tool, '-k', test_function, file]
            
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


if __name__ == '__main__':
    main()
