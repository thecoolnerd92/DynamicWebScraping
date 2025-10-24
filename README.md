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

<span style="color: red;">
    Note: I used asyncio.sleep() for selenium to make it asynchronous, so I could reuse the
    same main.py for both drivers.
</span>

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
  - Test opening new windows/ switching more

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
```
================================================================================================= 60 passed, 26 warnings in 2.30s =================================================================================================
Name                                     Stmts   Miss  Cover   Missing
----------------------------------------------------------------------
src/load_config.py                          18      0   100%
src/main.py                                112     10    91%   69-71, 170-174, 177-179
src/repository/web_driver_interface.py      32     10    69%   8, 12, 16, 20, 24, 28, 32, 36, 40, 44
src/service/nodriver_service.py            167     25    85%   77, 116, 124, 211-212, 256-257, 296, 300-332, 336-343, 347, 352
src/service/selenium_service.py            129      4    97%   126, 139-142
src/service/util_service.py                117      1    99%   102
----------------------------------------------------------------------
TOTAL                                      575     50    91%
```