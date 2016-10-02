#!/usr/bin/env python
# coding=utf-8
"""
calc.py - Phenny Calculator Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import web

r_result = re.compile(r'(?i)<A NAME=results>(.*?)</A>')
r_tag = re.compile(r'<\S+.*?>')

subs = [
    (' in ', ' -> '), 
    (' over ', ' / '), 
    ('£', 'GBP '), 
    ('€', 'EUR '), 
    ('\$', 'USD '), 
    (r'\bKB\b', 'kilobytes'), 
    (r'\bMB\b', 'megabytes'), 
    (r'\bGB\b', 'kilobytes'), 
    ('kbps', '(kilobits / second)'), 
    ('mbps', '(megabits / second)')
]

def calculate(phenny, input): 
    """Calculate things."""
    if not input.group(2):
        return phenny.reply("Nothing to calculate.")
    q = input.group(2)
    q = q.replace('\xcf\x95', 'phi') # utf-8 U+03D5
    q = q.replace('\xcf\x80', 'pi') # utf-8 U+03C0
    q = q.replace('÷', '/')
    q = web.quote(q)
    uri = 'https://www.calcatraz.com/calculator/api?c=' + q
    answer = web.get(uri)
    if answer: 
        answerindex = 1
        if (len(answer.split(";")) < 2):
            answerindex = 0
        answer = answer.split(";")[answerindex]
        answer = answer.replace('  ','')
        #answer = ''.join(chr(ord(c)) for c in answer)
        #answer = answer.decode('utf-8')
        #answer = answer.replace('\\x26#215;', '*')
        #answer = answer.replace('\\x3c', '<')
        #answer = answer.replace('\\x3e', '>')
        #answer = answer.replace('<sup>', '^(')
        #answer = answer.replace('</sup>', ')')
        #answer = web.decode(answer)
        if re.compile('answer').match(answer):
            return phenny.say('Sorry, no result.')
        else:
            return phenny.say(answer)
    else: 
        return phenny.say('Sorry, no result.')
calculate.commands = ['c','calc','calculate']
calculate.example = '.c 5 + 3'

def py(phenny, input):
    if not input.group(2):
        return phenny.reply(".py what?") 
    query = input.group(2)
    uri = 'http://tumbolia.appspot.com/py/'
    answer = web.get(uri + web.quote(query))
    if answer: 
        phenny.say(answer)
    else: phenny.reply('Sorry, no result.')
py.commands = ['py']

def wa(phenny, input): 
    if not input.group(2):
        return phenny.reply("No search term.")
    query = input.group(2)
    uri = 'http://tumbolia.appspot.com/wa/'
    answer = web.get(uri + web.quote(query.replace('+', '%2B')))
    answerindex = 1
    if (len(answer.split(";")) < 2):
        answerindex = 0
    answer = answer.split(";")[answerindex]
    if answer: 
        phenny.say(answer)
    else: phenny.reply('Sorry, no result.')
wa.commands = ['wa']

if __name__ == '__main__': 
    print(__doc__.strip())
