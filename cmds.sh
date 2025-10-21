#!/bin/bash

PATH=$1

coverage run --source=${PATH} -m pytest && coverage report -m

# GIT
# git remote add origin git@github.com:User/UserRepo.git
# git remote set-url origin git@github.com:User/UserRepo.git
