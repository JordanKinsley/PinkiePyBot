#!/usr/bin/env python
"""
admin.py - Phenny Admin Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

config and silence commands by Jordan Kinsley <jordan@jordantkinsley.org>
"""

import re

def join(phenny, input): 
    """Join the specified channel. This is an admin-only command."""
    # Can only be done in privmsg by an admin
    if input.sender.startswith('#'): 
        return
    if input.admin: 
        channel, key = input.group(1), input.group(2)
        if not key: 
            phenny.write(['JOIN'], channel)
        else: 
            phenny.write(['JOIN', channel, key])
join.rule = r'\.join (#\S+)(?: *(\S+))?'
join.priority = 'low'
join.example = '.join #example or .join #example key'

def autojoin(phenny, input): 
    """Join the specified channel when invited by an admin."""
    if input.admin: 
        channel = input.group(1)
        phenny.write(['JOIN'], channel)
autojoin.event = 'INVITE'
autojoin.rule = r'(.*)'

def part(phenny, input): 
    """Part the specified channel. This is an admin-only command."""
    # Can only be done in privmsg by an admin
    if input.sender.startswith('#'): 
        return
    if input.admin: 
        # TODO: add optional arguments for a part message
        phenny.write(['PART'], input.group(2).strip())
part.commands = ['part']
part.priority = 'high'
part.example = '.part #example'

def quit(phenny, input): 
    """Quit from the server. This is an owner-only command. Quit message is optional."""
    # Can only be done in privmsg by the owner
    if input.sender.startswith('#'): 
        return
    if input.owner: 
        # TODO: add optional arguments for a quit message
        a = input.group(2)
        if a: 
            phenny.write(['QUIT', a])
            __import__('os')._exit(0)
        else:
            phenny.write(['QUIT'])
            __import__('os')._exit(0)
quit.commands = ['quit']
quit.priority = 'high'
quit.example = '.quit message'

def msg(phenny, input): 
    # Can only be done in privmsg by an admin
    if input.sender.startswith('#'): 
        return
    a, b = input.group(2), input.group(3)
    if (not a) or (not b): 
        return
    if input.admin: 
        phenny.msg(a, b)
msg.rule = (['msg'], r'(#?\S+) (.+)')
msg.priority = 'low'

def me(phenny, input): 
    # Can only be done in privmsg by an admin
    if input.sender.startswith('#'): 
        return
    if input.admin: 
        msg = '\x01ACTION {0}\x01'.format(input.group(3))
        phenny.msg(input.group(2), msg)
me.rule = (['me'], r'(#?\S+) (.*)')
me.priority = 'low'

def config_get(phenny, input):
    """Get the config options for phenny or indicate """
    if not input.admin:
        phenny.say("Silly, you're not allowed to use this command!")
        return
    
    config_to_get = input.group(2).split(' ')[0]
    if config_to_get.lower() in ('password','youtube_api_key','serverpass','derpibooru_key'):
        phenny.say("Nuh uh! " + phenny.config.owner + " says that's a super-duper secret, and I promised to keep it!")
        return
    config_option = ""
    try:
        config_option = str(getattr(phenny.config, config_to_get))
        phenny.say("Looks like " + config_to_get + " is set to " + config_option)
    except AttributeError:
        phenny.say("Oops, looks like I don't have an option called " + config_to_get)
config_get.rule = (['config_get','c_get'], r'(.*)')
config_get.priority = 'low'

# options to never change
donotchange = ['nick','host','port','ssl','ipv6','owner','password','youtube_api_key','derpibooru_key']

def config_set(phenny, input):
    """Set a config option for phenny while the bot is running, ignoring options that can't or shouldn't be changed."""
    if not input.admin:
        phenny.say("Silly, you're not allowed to use this command!")
        return
    args = input.group(2).split(' ')
    config_to_set = args[0].lower()
    options = args[1:]
    if config_to_set.lower() in donotchange:
        phenny.say("Hey! " + phenny.owner + " says I'm not allowed to change that!")
        return
    if not hasattr(phenny.config, config_to_set):
        phenny.say("Oops, looks like I don't have an option called " + config_to_set)
        return
    existing_config = getattr(phenny.config, config_to_set)
    try:
        setattr(phenny.config, config_to_set, options)
        phenny.say("Woo! " + config_to_set + " has been updated to " + str(getattr(phenny.config, config_to_set)))
    except:
        setattr(phenny.config, config_to_set, existing_config)
        phenny.say("Oh no! " + config_to_set + " hasn't been updated! Sticking with the original value of "
            + existing_config + " instead.")
config_set.rule = (['config_set','c_set'], r'(.*)')
config_set.prioity = 'high'

'''
def silence(phenny, input):
    def ishostmask(subject):
        to_match = '(.*)!(.*)@(.*)'
        return re.compile(to_match).match(subject)
    # Can only be done in privmsg by an admin
    if input.sender.startswith('#'): 
        phenny.say('Nuh uh! Not here you can\'t!')
        return
    if input.admin:
        silence = 'SILENCE'
        if input.group(2) not in ('+','-'):
            phenny.msg(input.sender, 'Come on, plus or minus! Add or remove! You know this!')
        else:
            if input.group(2) is '+':
                #add to the silence list
                silence = silence + ' +'
            elif input.group(2) is '-':
                #remove from the silence list
                silence = silence + ' -'
            if input.group(3):
                #discard everything after the first space
                mask_to_silence = input.group(3).partition(' ')[0]
                phenny.msg(input.sender, "I'll be ignoring this (" + input.group(3).partition(' ')[2] + 
                    ") extra bit. Follow the rules and Auntie Pinkie will take care of everything else!")
                if ishostmask(mask_to_silence):
                    silence = silence + mask_to_silence + ' a'
                    phenny.msg(input.sender, '"' + silence + '" is being sent to the server')
                else:
                    phenny.msg(input.sender, 'That\'s not a hostmask, silly!')
        phenny.msg(input.sender, input.group(2) + ' group 2 input')
        phenny.msg(input.sender, input.group(3) + ' group 3 input')
silence.rule = (['silence'], r'(#?\S+) (.+)')
silence.priority = 'high'
silence.example = '.silence + foo!bar@buzz.com to add a silence or .silence - fizz!bang@widgets.net to remove a silence'
'''

if __name__ == '__main__': 
    print(__doc__.strip())
