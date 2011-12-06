#!/usr/bin/env python
"""
ping.py - Phenny Ping Module
Author: Sean B. Palmer, inamidst.com
About: http://inamidst.com/phenny/

Modified from ping.py by Amos

Modified by Jordan Kinsley
"""

import random

def hello(phenny, input): 
   greeting = random.choice(('Hi', 'Hey', 'Hello'))
   punctuation = random.choice(('', '!'))
   phenny.say(greeting + ' ' + input.nick + punctuation)
hello.rule = r'(?i)(hi|hello|hey) (I|Bli|Pi)nkie(Pie)?(Bot)?\b'

def sniff(phenny, input): 
   # TODO: rewrite responses
   sniffresponse = random.choice(('Hey! Do I know you?', 'Umm...', 'Do I smell funny - like \'haha\' funny or \'funny\' funny?', 'EEP!', 'ACTION prods ' + input.nick + '\'s nose.'))
   phenny.say(sniffresponse)
sniff.rule = r'(?i)(ACTION sniffs (I|Bli|Pi)nkie(Pie)?(Bot)?)'

def grope(phenny, input): 
   # TODO: rewrite responses
   groperesponse = random.choice(('I love hugs!', 'ACTION hugs ' + input.nick + 'SUPER hard.', 'ACK!', 'Hahaha, you suprised me, ' + input.nick + '!', 'I don\'t think I like that touch...', 'Gasp!'))
   phenny.say(groperesponse)
grope.rule = r'(?i)(ACTION runs over and squeezes (I|Bli|Pi)nkie(Pie)?(Bot)?)'

def flirt(phenny, input): 
     # TODO: rewrite responses
     attractresponse = random.choice(('I don\'t like you that way...', 'Sorry, I\'m not like that.', 'Flattering, but no.', 'Are you trying to flirt with me?', 'I\'d rather just be friends.', '...'))
     phenny.say(attractresponse)
flirt.rule = r'(?i)(ACTION winks at (I|Bli|Pi)nkie(Pie)?(Bot)?)'
# TODO: add more rules

def lick(phenny, input): 
   # TODO: Rewrite most responses
   lickresponse = random.choice(('...', 'What do I taste like? I want to know!', 'Ah!', 'Eep!', 'That tickles!', 'ACTION licks ' + input.nick + ' right back.', 'I don\'t like you that way...', 'Eww...','Waugh...', 'Ah!', '!', 'ACTION blushes.', 'ACTION pounces ' + input.nick + '.', 'ACTION steals ' + input.nick + '\'s virginity.', 'Hehe...'))
   phenny.say(lickresponse)
lick.rule = r'(?i)(ACTION licks (I|Bli|Pi)nkie(Pie)?(Bot)?)'

def growl(phenny, input): 
   # TODO: rewrite responses
   growlresponse = random.choice(('Silly puppy!', 'ACTION gives ' + input.nick + ' a slice of cake.', 'What did I do?', 'ACTION growls back.', 'Something wrong?'))
   phenny.say(growlresponse)
growl.rule = r'(?i)(ACTION growls at (I|Bli|Pi)nkie(Pie)?(Bot)?)'

def kiss(phenny, input):
    # TODO: add more responses
    kissresponse = random.choice(('ACTION blushes','What was that for?','ACTION leaps into the air in suprise.', 'ACTION pushes ' + input.nick + 'away.', 'ACTION bucks ' + input.name ' in the chest. Hard.', 'ACTION giggles.'))
    phenny.say(kissresponse)
kiss.rule = r'(?i)(ACTION kisses (I|Bli|Pi)nkie(Pie)?(Bot)?)'

def interjection(phenny, input): 
   phenny.say(input.nick + '!')
interjection.rule = r'(I|Bli|Pi)nkie(Pie)?(Bot)?!'
interjection.priority = 'high'
interjection.thread = False

def hugs(phenny, input):
   hugresponse = random.choice(('ACTION hugs ' + input.nick + ' back.', 'ACTION giggles.', 'Thanks, ' + input.nick + 'that felt really good!', 'Hugs for everypony!'))
   phenny.say(hugresponse)
hugs.rule = r'ACTION hugs (?i)(I|Bli|Pi)nkie(Pie)?(Bot)?'

def thanks(phenny, input):
   thanksresponse = random.choice(('No problemo', 'My pleasure', 'Hahah, you\'re welcome'))
   thankspuncuation = random.choice(('!', '.'))
thanks.rule = r'(?i)Thank( you|s|,)? (I|Bli|Pi)nkie(Pie)?(Bot)?'

# TODO: add these actions and appropriate responses
'''
Actions to add:
* pokes
* party
* cupcakes
* kicks
* tickles
* pranks
'''

if __name__ == '__main__': 
   print __doc__.strip()
