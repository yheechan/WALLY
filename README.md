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