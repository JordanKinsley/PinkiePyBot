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
hello.rule = r'(?i)(hi|hello|hey) $nickname\b'

def sniff(phenny, input): 
   # TODO: rewrite responses
   sniffresponse = random.choice(('Yeah... Don\'t do that...', 'Umm...', 'Do I smell funny or something?', 'Cut that out.', 'ACTION smacks ' + input.nick + '\'s nose.'))
   phenny.say(sniffresponse)
sniff.rule = r'(?i)(ACTION sniffs $nickname*)'

def grope(phenny, input): 
   # TODO: rewrite responses
   groperesponse = random.choice(('Hey! Don\'t touch me there!', 'ACTION uses Flamethrower on ' + input.nick + '!', 'ACK!', 'Keep your hands off me!', 'It would probably be best if you didn\'t touch me there again.', 'How about you don\'t touch me there again and I won\'t burn your flesh off.'))
   phenny.say(groperesponse)
grope.rule = r'(?i)(ACTION runs over and squeezes $nickname*)'

# TODO: remove
def supereffective(phenny, input): 
   supereffectiveresponse = random.choice(('ACTION cries.', 'Owwwwww...', 'Ouch! That huuuuuurts....', 'Please don\'t do that...', 'ACTION screams.', 'Why did you do thaaaaat?'))
   phenny.say(supereffectiveresponse)
supereffective.rule = r'ACTION uses (Force Palm|Aura Sphere|Close Combat|Focus Blast|Brick Break) on $nickname*'

# TODO: remove
def noteffective(phenny, input): 
   noteffectiveresponse = random.choice(('ACTION claps.', 'What exactly was that supposed to accomplish?', 'That tickles a bit.', 'Your Jedi mind tricks won\'t work on me.', '...What are you doing?', 'Oh, okay. Good luck with that.'))
   phenny.say(noteffectiveresponse)
noteffective.rule = r'ACTION uses Psychic on $nickname*'

# TODO: remove
def splash(phenny, input): 
   splashresponse = random.choice(('ACTION dries herself off.', 'Great. Now my hair is wet...', 'Ah! You got my hair wet.', 'Nice Magikarp impression.', 'I\'d rather stay dry, thank you.', 'No thanks. I\'m not thirsty.'))
   phenny.say(splashresponse)
splash.rule = r'ACTION uses Splash on $nickname*'

# TODO: remove
def tailwhip(phenny, input): 
   tailwhipresponse = random.choice(('ACTION pulls ' + input.nick + '\'s tail.', 'Get your tail out of my face.', 'No, I don\'t enjoy seeing your butt. Stop that.', 'ACTION \'s defense fell!', '1,15\'\'', 'That\'s a neat trick.'))
   phenny.say(tailwhipresponse)
tailwhip.rule = r'ACTION uses Tail Whip on $nickname*'

# TODO: remove
def healpulse(phenny, input): 
   healresponse = random.choice(('Thanks, ' + input.nick + '.', 'That feels nice....', ':>', 'Thank you for that.', 'Ah...'))
   phenny.say(healresponse)
healpulse.rule = r'ACTION uses Heal Pulse on $nickname*'

def flirt(phenny, input): 
     # TODO: rewrite responses
     attractresponse = random.choice(('I don\'t like you that way...', 'Sorry, I\'m not like that.', 'Flattering, but no.', 'Are you trying to flirt with me?', 'I\'d rather just be friends.', '...'))
     phenny.say(attractresponse)
flirt.rule = r'(?i)(ACTION uses (Attract|Captivate) on $nickname*)'
# TODO: add more rules

# TODO: remove
def attacked(phenny, input): 
   attackedresponse = random.choice(('ACTION uses Protect!', 'Ouch!', 'ACTION uses Flamethrower on ' + input.nick + '!', 'ACTION uses Night Daze on ' + input.nick + '!', 'ACTION uses Extrasensory on ' + input.nick + '!', 'ACTION uses Counter on ' + input.nick + '!'))
   phenny.say(attackedresponse)
attacked.rule = r'ACTION uses (Dragon Pulse|Metal Claw|ExtremeSpeed|Quick Attack) on $nickname*'

def lick(phenny, input): 
   # TODO: Rewrite most responses
   lickresponse = random.choice(('.', 'Ah!', 'Eep!', 'I\'ll rip out your tongue if you keep doing that.', 'ACTION rips out ' + input.nick + '\'s tongue.', 'I don\'t like you that way.', 'Eww...','Waugh...', 'Ah!', '!', 'ACTION blushes.', 'ACTION pounces ' + input.nick + '.', 'ACTION steals ' + input.nick + '\'s virginity.', 'Hee...'))
   phenny.say(lickresponse)
lick.rule = r'(?i)(ACTION licks $nickname*)'

def growl(phenny, input): 
   # TODO: rewrite responses
   growlresponse = random.choice(('Bad dog! Don\'t do that.', 'ACTION smacks ' + input.nick + ' with a newspaper.', 'What did I do?', 'ACTION growls back.', 'Something wrong?'))
   phenny.say(growlresponse)
growl.rule = r'(?i)(ACTION growls at $nickname*)'

def kiss(phenny, input):
    # TODO: add more responses
    kissresponse = random.choice(('ACTION blushes','ACTION kisses back','ACTION smacks ' + input.nick + '!'))
    phenny.say(kissresponse)
kiss.rule = r'(?i)(ACTION kisses $nickname*)'

def interjection(phenny, input): 
   phenny.say(input.nick + '!')
interjection.rule = r'$nickname!'
interjection.priority = 'high'
interjection.thread = False

# TODO: add these actions and appropriate responses
'''
Actions to add:
* hugs
* pokes
* party
* cupcakes
'''

if __name__ == '__main__': 
   print __doc__.strip()
