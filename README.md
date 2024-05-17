# WALLY: We Can LocaLize Your faulty lines

## How to use Docker
```
docker image build -t test .
```
```
docker run -p 2222:2222 -t -i test
```
It will automatically set up bugsinpy.

---
In docker, (now testcase_check only support spacy)
```
bugsinpy-checkout -p spacy -v 0 -i 5
cd mutpy/lib
python3 testcase_checker.py
```
it will show all the test cases in spacy.

## Executing ``wally.py``

usage:
```
./wally.py --source-dir <project source directory> --test-dir <test case directory> --testing-tool <testing tool>
```
or
```
./wally.py -s <project source directory> -t <test case directory> -T <testing tool>
```

For more info,
```
./wally.py --help

usage: wally.py [-h] --source-dir SOURCE_DIR --test-dir TEST_DIR [--testing-tool {pytest,unittest}] [--output-dir OUTPUT_DIR] [--save-pre-analysis]

Pre-analysis for MBFL

options:
  -h, --help            show this help message and exit
  --source-dir SOURCE_DIR, -s SOURCE_DIR
                        Root directory of sources to be tested
  --test-dir TEST_DIR, -t TEST_DIR
                        Root directory of test cases
  --testing-tool {pytest,unittest}, -T {pytest,unittest}
                        Testing tool to be used. Default is pytest
  --output-dir OUTPUT_DIR, -o OUTPUT_DIR
                        Directory of pre-analysis results will be stored (default: ./pre-analysis/)
  --save-pre-analysis, -S
                        Save pre-analysis results as a file
```

### Example

```
./wally.py --source-dir ./examples/chess/chess --test-dir ./examples/chess/tests --testing-tool pytest
```

## What it does!

### 1. Pre-analysis stage
Wally first executes the each test cases against the target subject. During this stage, wally retrieves the results (pass or fail) & coverage of each individual test case.
    * Currently, `pytest` and `unittest` are supported as testing tools. Default tool is `pytest`.

