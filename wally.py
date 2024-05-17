#!/usr/bin/python3
import sys
import argparse
import lib.analysis as analysis
import lib.mbfl as mbfl
import json
from pathlib import Path

available_test_tools = ['pytest', 'unittest']

def main():
    parser = make_parser()
    args = parser.parse_args()

    # CONVERT USER INPUT DIRECTORY PATHS TO PATHLIB
    print(args.target)
    source_dir = Path(args.target[0]).resolve()
    test_dir = Path(args.unit_test[0]).resolve()
    testing_tool = args.runner
    output_dir = Path('pre-analysis').resolve()
    save_pre_analysis = args.save_pre_analysis

    # RUN PRE-ANALYSIS (MEASURE INITAL TEST CASE RESULTS AND COVERAGE)
    test_results = analysis.main(
        source_dir, test_dir,
        testing_tool, output_dir,
        save_pre_analysis
    )
    json_file = Path('pre-analysis/test_results.json')
    test_results = json.load(json_file.open())

    # RUN MUTATION TESTING
    sys.path.append('mutpy/')
    #sys.path.append(__file__[:-9] + "/mutpy")
    from mutpy import commandline
    mbfl_results = commandline.main(sys.argv[1:], test_results)

    if args.save_mbfl_results:
        with open('mbfl_results.json', 'w') as f:
            json.dump(mbfl_results, f, indent=4)

    mbfl_file = Path('mbfl_results.json')

    mbfl_results = json.load(mbfl_file.open())
    mbfl.calc_susp_score(mbfl_results)
    
    if args.save_mbfl_results:
        with open('mbfl_results.json', 'w') as f:
            json.dump(mbfl_results, f, indent=4)


def make_parser():
    parser = argparse.ArgumentParser(description='Pre-analysis for MBFL')
    parser.add_argument('--target', '-t', type=str, nargs='+', help='target module or package to mutate')
    # parser.add_argument('--source-dir', '-s', type=str, required=True,
    #                     help='Root directory of sources to be tested')
    parser.add_argument('--unit-test', '-u', type=str, nargs='+',
                        help='test class, test method, module or package with unit tests')
    # parser.add_argument('--test-dir', '-t', type=str, required=True,
    #                     help='Root directory of test cases')
    parser.add_argument('--runner', type=str, choices=['unittest', 'pytest'], default='unittest',
                        metavar='RUNNER', help='test runner')
    # parser.add_argument('--testing-tool', '-T', type=str, choices=available_test_tools, default='pytest', 
    #                     help='Testing tool to be used. Default is pytest')
    parser.add_argument('--save-pre-analysis', '-S', default=False, action='store_true',
                        help='Save pre-analysis results as a file')
    parser.add_argument('--save-mbfl-results', '-M', default=False, action='store_true',
                        help='Save MBFL results as a file')
    parser.add_argument('--show-mutants', '-m', action='store_true', help='show mutants source code')
    parser.add_argument('--pytest-function-timeout', type=int, default=10, 
                        help='set timeout for each testcase function')
    parser.add_argument('--pytest-session-timeout', type=int, default=600, 
                        help='set timeout for each test module')
    return parser



if __name__ == "__main__":
    main()