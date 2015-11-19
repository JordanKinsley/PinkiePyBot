#!/usr/bin/env python
"""
seen.py - Phenny seen module
"""
import sqlite3 as lite
import os
import datetime
import time
import re

def db_connect(db):
    return lite.connect(db, check_same_thread = False, detect_types=lite.PARSE_DECLTYPES)

def setup(phenny):
    seen_db = os.path.join(os.path.expanduser('~/.phenny'), 'seen.db')
    seen_conn = db_connect(seen_db)
    c = seen_conn.cursor()
    c.execute('''create table if not exists seen(
        nick    varchar(31) NOT NULL PRIMARY KEY,
        channel varchar(31) NOT NULL,
        message text,
        event   varchar(10) NOT NULL,
        time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
        );''')
    c.close()
    seen_conn.commit()
    seen_conn.close()
setup.thread = False

def smart_truncate(content):
    suffix='...'
    length=int(150)
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' ', 1)[0]+suffix

def seen(phenny, input):
    """Gives when a user was last seen."""
    inputnick = input.group(2)
    regex = re.compile("\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
    inputnick = regex.sub("", inputnick)
    inputnick = inputnick.replace('\x0f','')
    inputnick = inputnick.replace('\002','')
    inputnick = inputnick.replace('\010','')
    inputnick = inputnick.replace('\037','')
    inputnick = inputnick.replace('\017','')
    inputnick = inputnick.replace('\026','')
    inputnick = inputnick.replace('\007','')
    inputnick = inputnick.replace('\035','')
    inputnick = inputnick.rstrip()
    
    seen_db = os.path.join(os.path.expanduser('~/.phenny'), 'seen.db')
    seen_conn = db_connect(seen_db)
    conn = db_connect(seen_db)
    c = conn.cursor()
    query = (inputnick,)
    c.execute("SELECT * FROM seen WHERE nick LIKE ?;", query)
    resultsun = c.fetchall()
    try:
        results = resultsun[0]
    except:
        nick = None
    
    try:
        nick = results[0]
        channel = results[1]
        message = results[2]
        event = results[3]
        seentimeun = results[4]
    except:
        nick = None
    if not inputnick:
        phenny.say ("\x01ACTION pokes " + input.nick + "\x01")
        phenny.say("Are you broken?")
        phenny.say("I need a nick for that command")
    elif input.nick == inputnick:
        phenny.say("Silly, that's you!")
    elif inputnick == phenny.nick:
        phenny.say("Silly, that's me!")
    elif not nick:
        phenny.say("Sorry I haven't seen " + inputnick)
    else:
        
        seentime = seentimeun.strftime('%A %B %d, %G at %I:%M:%S %p GMT')
        message = message.replace('\x01ACTION','/me')
        message = message.replace('\x01','')
        message = smart_truncate(message)
        message = message + '\017'
        if event == "PRIVMSG":
            phenny.say(nick + " was last seen in " + channel + ' saying "' + message + '" on ' + seentime)
        elif event == "JOIN":
            phenny.say(nick + " was last seen joining " + channel + " on " + seentime)
        elif event == "PART":
            phenny.say(nick + " was last seen leaving " + channel + ' with message "' + message + '" on ' + seentime)
        elif event == "QUIT":
            phenny.say(nick + ' was last seen quitting with message "' + message + '" on ' + seentime)
    c.close()
seen.commands = ['seen']
seen.example = ".seen somenick"

def seenstore(phenny, input, event):
    nick = input.nick
    channel = input.sender
    if event == "JOIN":
        message = None
    else:
        message = input.group()
    seen_db = os.path.join(os.path.expanduser('~/.phenny'), 'seen.db')
    seen_conn = db_connect(seen_db)
    conn = db_connect(seen_db)
    c = conn.cursor()
    entry = (nick, channel, message, event)
    c.execute("INSERT OR REPLACE INTO seen(nick, channel, message, event) VALUES(?, ?, ?, ?)", entry)
    conn.commit()
    c.close()
    conn.close()

def seenmsg(phenny, input):
    event = "PRIVMSG"
    seenstore(phenny, input, event)
seenmsg.rule = r'(.*)'
seenmsg.priority = 'low'

#def seenjoin(phenny, input):
#    event = "JOIN"
#    seenstore(phenny, input, event)
#seenjoin.event = 'JOIN'
#seenjoin.rule = r'(.*)'
#seenjoin.priority = 'low'

#def seenquit(phenny, input):
#    event = "QUIT"
#    seenstore(phenny, input, event)
#seenquit.event = 'QUIT'
#seenquit.rule = r'(.*)'
#seenquit.priority = 'low'

#def seenpart(phenny, input):
#    event = "PART"
#    seenstore(phenny, input, event)
#seenpart.event = 'PART'
#seenpart.rule = r'(.*)'
#seenpart.priority = 'low'
