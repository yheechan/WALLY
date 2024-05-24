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
./wally.py --target <project source directory> --unit-test <test case directory> --runner <testing tool> --save-pre-analysis -m
```

For more info,
```
./wally.py --help

usage: wally.py [-h] [--target TARGET [TARGET ...]] [--unit-test UNIT_TEST [UNIT_TEST ...]] [--runner RUNNER] [--output-dir OUTPUT_DIR]
                [--save-pre-analysis] [--show-mutants]

Pre-analysis for MBFL

options:
  -h, --help            show this help message and exit
  --target TARGET [TARGET ...], -t TARGET [TARGET ...]
                        target module or package to mutate
  --unit-test UNIT_TEST [UNIT_TEST ...], -u UNIT_TEST [UNIT_TEST ...]
                        test class, test method, module or package with unit tests
  --runner RUNNER       test runner
  --output-dir OUTPUT_DIR, -o OUTPUT_DIR
                        Directory of pre-analysis results will be stored (default: ./pre-analysis/)
  --save-pre-analysis, -S
                        Save pre-analysis results as a file
  --show-mutants, -m    show mutants source code
```

### Example

```
./wally.py --target ./examples/chess/chess --unit-test ./examples/chess/tests --runner pytest -m
```

## What it does!

### 1. Pre-analysis stage
Wally first executes the each test cases against the target subject. During this stage, wally retrieves the results (pass or fail) & coverage of each individual test case.
    * Currently, `pytest` and `unittest` are supported as testing tools. Default tool is `pytest`.

