# Dynamic Web Scraping Module 
```
Program: main.py
Version 1.0.0 (python 3.7+ compatible)
Usage: python src/main.py <commands>
```
A robust, reusable module for web scraping with the scraping library abstracted 
away so it can be easily updated/ changed as needed.
Update the config in the settings.py file to run with a different configuration.
Set your driver option (selenium or nodriver) in the config (defaults to nodriver)

### Current Options
  - selenium (my current preferred option for most cases)
    - pros
      - robust library with actions to mimic real user actions
      - simple/ easy to use methods
    - cons
      - failed pixelscan bot detection check
  - nodriver
    - pros
      - passes pixelscan bot detection check
    - cons
      - seems to lack some user actions like scrolling to an item on the page
      - requires a lot of custom js code to perform some steps correctly
     

### To Do
  - complete/ unit tests (selenium_service)

### Env Setup 
```
% python3 -m venv .venv
% pip install -r requirements
```

### Run Unit Tests

```
% coverage run --source=./src -m pytest && coverage report -m
```

### Coverage
```================================================================================================= 44 passed, 24 warnings in 1.63s =================================================================================================
Name                                     Stmts   Miss  Cover   Missing
----------------------------------------------------------------------
src/main.py                                112     10    91%   69-71, 170-174, 177-179
src/repository/web_driver_interface.py      35     11    69%   8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48
src/service/nodriver_service.py            166     25    85%   74, 113, 121, 208-209, 253-254, 291, 295-327, 331-338, 342, 347
src/service/selenium_service.py            132    106    20%   20-57, 61-64, 67, 70-86, 89-108, 113-125, 131-141, 145-157, 161-165, 169-177, 181-185, 189-190
src/service/util_service.py                120      1    99%   105
----------------------------------------------------------------------
TOTAL                                      565    153    73%

```