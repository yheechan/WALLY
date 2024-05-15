#!/usr/bin/python3
import sys
import argparse


# --save-failinglines

# failing_lines = {
#     'tc1': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
# }

# import json
# json.dump(failing_lines, open('failing_lines.json', 'w'))

# executes mutpy
sys.path.append('mutpy/')
from mutpy import commandline
commandline.main(sys.argv[1:])