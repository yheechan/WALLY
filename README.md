# WALLY: We cAn LocaLize faultY line with Mutations

![wally_lens](https://github.com/yheechan/WALLY/assets/97732494/48c77a85-ecaf-4c4a-9a4b-8ba5ffaca3f8)

## Features

WALLY is a fault localization tool using MBFL. It computes the suspicioius socore uisng MUSE formula and visualize it by coloring line accordint to the rank of scores.

## Requirements
```
pip install -r requirements.txt
```
- yaml
- pytest
- pytest-timeout
- astmonkey
- termcolor
- coverage


## Configuration

To execute WALLY, configuration file named `wally.json` should be added in your project root directory:
```json
{
    "target" : "project source directory",
    "unit_test" : "project unit-test case directory",
    "tool" : "testing tool"
}
```
Currently, WALLY support `pytest` as a testing tool.

## How to run WALLY

Once the configuration file is set up, run wally by clicking the wally button in the top right corner of the screen.
When wally completes the calculation, you'll see the results, with each line colored according to computed suspicion scores.
