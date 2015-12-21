#!/usr/bin/env python
'''
bestpony.py - PinkiePyBot best pony tracker
(C) 2012 Jordan T Kinsley (jordan@jordantkinsley.org)
GPLv2 or later

This module will let Pinkie inform users of the best pony or confirm or
deny their suspected best ponies. 
'''

import random, re, sys, time, sqlite3

nicks_in_mem = sqlite3.connect(':memory:', check_same_thread = False)
ponies = ('Twilight Sparkle','Rarity','me','Applejack','Fluttershy','Sunset Shimmer', 'Maud Pie')
ponies_alt = ('Princess Celestia','Princess Luna','Princess Cadance','Shining Armor','Roseluck','Trixie','Sweetie Belle','Apple Bloom','Scootaloo','Mr Cake','Mrs Cake','Pound Cake','Pumpkin Cake','Granny Smith','Big Macintosh','Lyra','Bon Bon')
not_best_ponies = ('Flash Sentry')
not_ponies = ('Discord','Philomena','Spike','Gilda','Gummy')
pony_map = {'Twilight': 'Twilight Sparkle', 'Rainbow': 'Rainbow Dash', 'Dash': 'Rainbow Dash', 'Pinkie': 'Pinkie Pie', 'Sunset': 'Sunset Shimmer', 'Bland Sentry': 'Flash Sentry', 'Flash': 'Flash Sentry', 'Celestia': 'Princess Celestia', 'Luna': 'Princess Luna', 'Cadance': 'Princess Cadance', 'Mr. Cake': 'Mr Cake', 'Mrs. Cake': 'Mrs Cake', 'Big Mac': 'Big Macintosh'}
superlatives = ('cool', 'rad', 'sweet', 'awesome', 'amazing', 'cool', 'much the best')

def setup(phenny):
    nicks_in_mem = sqlite3.connect(':memory:', check_same_thread = False)
    nicks_in_mem.execute('''
        create table if not exists nicks(
            nick    varchar(31) NOT NULL PRIMARY KEY
        );''')
    nicks_in_mem.commit()
setup.thread = False

def best_pony(phenny, input):
    if input.nick in phenny.config.user_ignore:
        return
    best_pony_response = "Oh, that's easy, it's " + random.choice(ponies_alt) + "! No... wait, it's definitely " + random.choice(ponies) + "! "
    phenny.say(best_pony_response)
    phenny.say("I'm kidding, of course! It's you, silly!")
best_pony.rule = r'(?i)(I|Bli|Pi)nkie(Pie)?(Bot)?, who(\'s| is)( the)? best pony(\?)?'

def is_best_pony(phenny, input):
    more_nicks = False
    
    if phenny.config.debug:
        print(type(phenny.channel_nicks), file=sys.stderr)
    if input.nick in phenny.config.user_ignore:
        return
    rule_text = input.group(0) # unfortunately, unlike the image.py module, 
    # we're just using a rule, not a command. All of our input is in group 0
    find_pony = re.compile("(?i)(I|Bli|Pi)nkie(Pie)?(Bot)?(,|:)? is (?P<pony>.*?)( the)? best pony(\?)?")
    try:
        alleged_best_pony = re.match(find_pony, rule_text).group('pony').title()
    except AttributeError:
        if re.match("(?i)(I|Bli|Pi)nkie(Pie)?(Bot)?(,|:)? are you( .*)?( the)?( .*)?best pony(\?)?", rule_text):
            alleged_best_pony = 'Pinkie Pie'
        else:
            phenny.say('Uh, I\'m sorry, ' + input.nick + ' but I got a little confused there. Ask me again?')
            return
    
    # start prep work for getting the nick list and using it
    # double check that more_nicks is set to false before we start
    more_nicks = False
    # clear the channel_nicks list and start fresh
    
    # now send the NAMES command for this channel; we need to send a raw command to the server, hence the "write" function
    # to save time, we are only asking for this channel, not all the nicks the bot can see
    if phenny.config.debug:
        print("triggering 353/366 series in " + input.sender, file=sys.stderr)
    phenny.write(['NAMES {0}'.format(input.sender)])
    
    if phenny.config.debug:
        print("sleeping 1/2 sec", file=sys.stderr)
        print("channel_nicks: " + str(phenny.channel_nicks), file=sys.stderr)
    time.sleep(0.5)
    while more_nicks:
        if phenny.config.debug:
            print("Waiting until 366 for " + input.sender, file=sys.stderr)
        time.sleep(0.5)
    channel_nicklist = phenny.channel_nicks.copy()
    if not channel_nicklist:
        try:
            for row in nicks_in_mem.execute('SELECT nick FROM nicks'):
                channel_nicklist.append(row[0])
            if phenny.config.debug:
                print("using memory DB for nicklist", file=sys.stderr)
        except sqlite3.OperationalError:
            pass
    if phenny.config.debug:
        print("channel_nicks: " + str(phenny.channel_nicks), file=sys.stderr)
    if phenny.config.debug:
        print("channel_nicklist: " + str(channel_nicklist), file=sys.stderr)
    # clear the channel_nicks again
    phenny.channel_nicks.clear()
    if phenny.config.debug:
        print("channel list cleared", file=sys.stderr)
    
    if alleged_best_pony.lower() in [nick.lower() for nick in channel_nicklist]:
        if alleged_best_pony in phenny.config.admins:
            phenny.say("Oh yeah! " + alleged_best_pony + " is the best! Rock on!")
        else:
            phenny.say("Yeah, " + alleged_best_pony + " is pretty " + random.choice(superlatives) + "!")
        channel_nicklist.clear()
        return
    if alleged_best_pony in pony_map:
        alleged_best_pony = pony_map[alleged_best_pony]
    if alleged_best_pony == 'Rainbow Dash':
        phenny.say("Ha ha, yeah! Dashie's pretty cool.")
    elif alleged_best_pony == 'Pinkie Pie':
        phenny.say("Aw, that's sweet, " + input.nick + "! I think I'm pretty swell, too.")
    elif alleged_best_pony in ponies:
        phenny.say("Ha ha, yeah! " + alleged_best_pony + " is my best friend! I love her!")
    elif alleged_best_pony in ponies_alt:
        phenny.say("Ha ha, yeah! " + alleged_best_pony + " is pretty " + random.choice(superlatives) + "!")
    elif alleged_best_pony in not_ponies:
        phenny.say("Ha ha, you're silly! " + alleged_best_pony + " isn't a pony!")
    elif alleged_best_pony in not_best_ponies:
        phenny.say("Erm... no. No way! " + alleged_best_pony + " is totally not cool.")
    else:
        phenny.say("I'm sorry, " +  input.nick + " but I don't know " + alleged_best_pony + " very well. I'm sure they're pretty neat!")
    
is_best_pony.rule = r'(?i)(I|Bli|Pi)nkie(Pie)?(Bot)?(,|:)? (is|are you) (?#pony)(.*)( the)?( .*)?best pony(\?)?'
is_best_pony.thread = True

def names(phenny, input):
    if not input.admin: return
    phenny.say('OK, I\'ll ask for who\'s here!')
    phenny.write(['NAMES {0}'.format(input.sender)])
names.commands = ['names']

def names_on_353(phenny, input):
    if phenny.config.debug:
        print("353 event triggered", file=sys.stderr)
    
    # if we're running 3.3 or later, we can use .clear(), otherwise it raises an attribute error
    phenny.channel_nicks.clear()
    
    more_nicks = True
    e353_bytes = input.bytes.split()
    e353_return = []
    for nick in e353_bytes:
        nick = nick.lstrip('~@%&+')
        e353_return.append(nick)
    #phenny.msg('#PinkiePieBot-dev', 'Nicks with prefixes removed: ' + str(e353_return))
    if phenny.config.debug:
        print("event 353 nicks: " + str(e353_return), file=sys.stderr)
    phenny.channel_nicks.extend(e353_return)
    
    try:
        nicks_in_mem.execute('''DELETE FROM nicks;''')
        for nick in e353_return:
            nicks_in_mem.execute('''INSERT INTO nicks(nick) VALUES (?); ''', (nick,))
        nicks_in_mem.commit()
    except sqlite3.OperationalError:
        pass
    
    if phenny.config.debug:
        print("channel_nicks in names_on_353: " + str(phenny.channel_nicks), file=sys.stderr)
names_on_353.event = '353'
names_on_353.rule = r'.*'
names_on_353.priority = 'high'
names_on_353.thread = True

def on_366(phenny, input):
    #phenny.msg('#PinkiePieBot-dev', 'Hey, looks like server said that\'s everyone!')
    if phenny.config.debug:
        print('received 366', file=sys.stderr)
    more_nicks = False
on_366.event = '366'
on_366.rule = r'.*'
on_366.priority = 'high'
on_366.thread = True
