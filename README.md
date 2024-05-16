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

## Get test case results and coverage information before mutation

`lib/analysis.py` runs a testing tool on the project's test cases and saves the results along with the coverage as a json file in `./pre-analysis/test_results.json`.

Currently, `pytest` and `unittest` are supported as testing tools. Default tool is `pytest`

usage:
```
python3 lib/analysis.py --source-dir <project source directory> --test-dir <test case directory> --testing-tool <testing tool>
```
or
```
python3 lib/analysis.py -s <project source directory> -t <test case directory> -T <testing tool>
```

For more info,
```
python3 lib/analysis.py --help
```

### Example

```
python3 lib/analysis.py --source-dir ./examples/chess/chess --test-dir ./examples/chess/tests --testing-tool pytest
```

