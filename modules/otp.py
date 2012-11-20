#!/usr/bin/python3
'''
otp.py - Pinkie's One True Pair module
Copyright 2012 by Jordan T Kinsley <jordan@jordantkinsley.org>
Licensed under the Eiffel Forum License 2

https://github.com/JordanKinsley/PinkiePyBot
'''

import os, sqlite3, random
import web
from bs4 import BeautifulSoup as Soup

# TODO: record an OTP
# TODO: retrieve an OTP
# TODO: randomly pair channel members
# TODO: query the MLP Wikia for random crack ships

def otp(phenny, input):
    '''.otp <character> x <character>: stores a One True Pairing; .otp retrieves a random pairing; .otp <character> retrieves a pairing with <character>'''
    #TODO: get the arguments (if any) and figure out what to do
    pairing = input.group(2)
    first, second = pairing.lower().split(' x ')
otp.commands = ['onetruepair','otp']
