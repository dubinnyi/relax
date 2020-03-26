#!/usr/bin/bash

# require file with groupnames

#
# $1 - file with data
# $2 - file with groupnames
# $3 - string with commands for fit data
#

while read LINE
    do ./fit_data.py $1 -g $LINE $3
done < $2