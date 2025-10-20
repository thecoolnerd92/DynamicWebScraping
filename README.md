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
  - complete/ fix unit tests (util and settings are done)

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
coverage stats will go here once completed
```