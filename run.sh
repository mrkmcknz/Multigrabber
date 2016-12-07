#! /bin/bash

rm -f $(ls | grep -i 'input-')
split -l 200 data/input.txt input-

for i in input-[a-z][a-z]; do
    rm $i
    nohup python run.py -i $i &
done
