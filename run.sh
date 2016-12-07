#! /bin/bash

rm -f $(ls | grep -i 'input-')
split -l 200 data/input.txt input-
parallel python run.py -i ::: input-[a-z][a-z]
