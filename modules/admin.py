#!/usr/bin/env python
"""
admin.py - Phenny Admin Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

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
    """Quit from the server. This is an owner-only command."""
    # Can only be done in privmsg by the owner
    if input.sender.startswith('#'): 
        return
    if input.owner: 
        # TODO: add optional arguments for a quit message
        phenny.write(['QUIT'])
        __import__('os')._exit(0)
quit.commands = ['quit']
quit.priority = 'high'

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

def silence(phenny, input):
    '''.silence <+|-><hostmask> <options> - server-side silence command'''
    # This might only work for Canternet. Check your network's help for /silence
    # TODO: add a text file with a list of silenced nicks to be loaded on connect
    if input.sender.startswith('#'):
        return
    if input.admin:
        if not input.groups():
            phenny.write(['SILENCE'])
        hostmask = input.group(1)
        options = input.group(2)
        phenny.write(['SILENCE', hostmask, options])
silence.commands = ['silence']
silenece.priority = 'high'

def silence_reply(phenny, input):
    phenny.msg(phenny.config.owner, input.groups())
silence_reply.event = '272'

if __name__ == '__main__': 
    print(__doc__.strip())
