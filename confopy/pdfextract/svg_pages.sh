#!/bin/bash

for i in {0..11} 
do 
    python domtest.py $i > page$i.svg 
done
