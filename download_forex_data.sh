#!/usr/bin/env bash

CURRENCY_PAIR=$1
START_DATE=$2
END_DATE=$3

duka $CURRENCY_PAIR -s $START_DATE -e $END_DATE -f input/ --header
