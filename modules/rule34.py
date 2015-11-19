#!/usr/bin/python3
'''
rule34.py - rule 34 module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>

e621 and twentypercentcooler modifications by Jordan Kinsley <jordan@jordantkinsley.org>
'''

# TODO: extract duplicate and make it into a seperate function. 
# code duplication is killing this module.

from urllib.parse import quote as urlquote
from urllib.parse import quote_plus as urlquoteplus
from urllib.error import HTTPError
from tools import GrumbleError
import web
import json
import xml.etree.ElementTree as ET # parsing xml not html
from random import choice 
import time
import calendar

def rule34(phenny, input):
    """.rule34 <query> - Rule 34: If it exists there is porn of it."""
    
    if input.nick in phenny.config.user_ignore:
        return
    
    if check_nsfw(phenny, input.sender, None, input.nick):
        return
    q = input.group(2)
    if not q:
        phenny.say(rule34.__doc__.strip())
        return

    try:
        req = web.get('http://rule34.xxx/index.php?page=dapi&s=post&q=index&tags={0}'.format(urlquote(q))) #Lets use XML!
    except (HTTPError, IOError):
        raise GrumbleError("THE INTERNET IS FUCKING BROKEN. Please try again later.")

    results = ET.fromstring(req)

    if len(results) <= 0:
        phenny.reply("Huh. rule34.xxx is missing {0}".format(q))
        return

    try:
        link = (choice(results).attrib['file_url'])
    except AttributeError:
        raise GrumbleError("THE INTERNET IS BROKEN. Please try again later.")

    response = '!!NSFW!! -> {0} <- !!NSFW!!'.format(link)
    phenny.reply(response)
rule34.commands = ['r34', 'rule34']

def e621(phenny, input):
    '''.e621 <query> - returns a random image for any query from e621.net (all links tagged as NSFW). 
    Query must be formatted like a normal e621 search: all tags have their spaces replaced with 
    underscores.'''
    
    if input.nick in phenny.config.user_ignore:
        return
    
    q = input.group(2)
    if not q:
        phenny.say(e621.__doc__.strip())
        return
    sfw, q = check_rating(phenny, input.sender, q, input.nick)

    # we're going to assume users know what to search for. :S
    link = get_boru(phenny,'e621',q)
    if link :
        if sfw:
            link = link.replace('e621','e926') #added e in case 621 is in the id
        phenny.reply(link)
e621.commands = ['e621']

def tpc(phenny, input):
    '''.tpc <query> - returns the image for any query from twentypercentcooler.net 
    (all links tagged as NSFW)Query must be formatted like a normal twentypercentcooler search: all 
    tags have their spaces replaced with underscores.'''
    
    if input.nick in phenny.config.user_ignore:
        return
    
    q = input.group(2)
    
    if not q:
        phenny.say(tpc.__doc__.strip())
        return
    sfw, q = check_rating(phenny, input.sender, q, input.nick)

    # we're going to assume users know what to search for. :S
    link = get_boru(phenny,'twentypercentcooler',q)
    if link :
        phenny.reply(link)

tpc.commands = ['tpc', 'twentypercentcooler', 'ponies']

def derpibooru_search(query, phenny):
    query = query.replace('!', '')
    query = web.quote(query)
    if hasattr(phenny.config, 'derpibooru_key'):
        uri = 'https://derpibooru.org/search.json?q=' + query + '&key=' + phenny.config.derpibooru_key
    else:
        uri = 'https://derpibooru.org/search.json?q=' + query
    rec_bytes = web.get(uri)
    jsonstring = json.loads(rec_bytes)
    dhits = jsonstring['total']
    if dhits > 0:
        results = choice(jsonstring['search'])
        url = 'https:' + results['image']
        uploader = results['uploader']
        uploaded = results['created_at']
        try:
            import dateutil.parser
            isdateutil = True
            dt = dateutil.parser.parse(uploaded)
            timestamp1 = calendar.timegm(dt.timetuple())
            timestamp1 = time.gmtime(timestamp1)
            uploadedformat = time.strftime('%A %B %d, %G at %I:%M:%S %p',timestamp1)
        except:
            isdateutil = False
        if isdateutil is True:
            return url + ' uploaded by ' + uploader + ' on ' + uploadedformat
        else:
            return url + ' uploaded by ' + uploader
    else:
        return

def derpibooru(phenny, input):
    '''Gets images from Derpibooru, needs an API key in the config to get NSFW images'''
    query = input.group(2)
    if not query: return phenny.reply('.derpi what?')

    uri = derpibooru_search(query, phenny)
    if uri: 
        phenny.say("Here's what I got, " + input.nick + ": " + uri)
        if not hasattr(phenny.bot, 'last_seen_uri'):
            phenny.bot.last_seen_uri = {}
        phenny.bot.last_seen_uri[input.sender] = uri
    else: phenny.say("Sorry " + input.nick + ", I couldn't find anything for '%s'." % query)
derpibooru.commands = ['derpi','db','derpibooru']
derpibooru.example = '.derpi sweetie belle,fluttershy'

##
# Helper Functions
##
def get_boru(phenny, site, tags):
    try:
        req = web.get("http://{0}.net/post/index.json?tags={1}".format(site,urlquoteplus(tags)))
    except (HTTPError, IOError):
        phenny.say('Oopsies, looks like the Internet is broken.')
        return
    
    results = json.loads(req, encoding='utf-8')

    if len(results) <= 0:
        phenny.reply("Huh. {0} is missing {1}".format(site,tags))
        return
    
    try:
        link = 'http://{0}.net/post/show/{1}/'.format(site,choice(results)['id'])
        if site is 'e621':
            image = (choice(results)['file_url'])
        if site is 'twentypercentcooler':
            image = 'http://twentypercentcooler.net' + (choice(results)['file_url'])
    except AttributeError:
        phenny.say('Oopsies, looks like the Internet is broken.')

    tags = results[0]
    rating = tags['rating']
    if rating in ('q','e'):
        link = '!!NSFW!! -> {0} <- !!NSFW!!'.format(link)
        image = '!!NSFW!! -> {0} <- !!NSFW!!'.format(image)
    return image

def check_rating(phenny, sender, q, nick):
    sfw = False
    if check_nsfw(phenny, sender, q, nick):
        if q.lower() in ('rating:explicit','rating:questionable','rating:e','rating:q'):
            q = q.replace('rating:explicit','rating:safe')
            q = q.replace('rating:questionable','rating:safe')
            q = q.replace('rating:e','rating:s')
            q = q.replace('rating:q','rating:s')
        else: 
            q = q + ' rating:safe'
        sfw = True
    return sfw, q


def check_nsfw(phenny, sender, q, nick):
    '''return true if this channel is SFW; false if NSFW'''
    nsfw_channels = []
    try:
        nsfw_channels = phenny.config.nsfw
    except:
        return True # if no one configured any NSFW channels, let's assume they're all SFW
    if sender not in nsfw_channels:
        if not q or q.lower() in ('rating:explicit','rating:questionable','rating:e','rating:q'):
            # if someone is legit trying to break the rules by searching for an explicit image
            phenny.msg('MemoServ', 'SEND {0} {2} in {1} tried to break the rules!'.format(phenny.config.owner, sender, nick))
        return True
    else: return False

if __name__ == '__main__':
    print(__doc__.strip())
