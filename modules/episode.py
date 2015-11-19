#!/usr/bin/env python
"""
episode.py - Phenny MLP Episodes Module

"""

import re
import web
import json
import string
import ast
import calendar
import time

class Grab(web.urllib.request.URLopener):
    def __init__(self, *args):
        self.version = 'Mozilla/5.0 (CompuBot)'
        web.urllib.request.URLopener.__init__(self, *args)
        self.addheader('Referer', 'https://github.com/sbp/phenny')
    def http_error_default(self, url, fp, errcode, errmsg, headers):
        return web.urllib.addinfourl(fp, [headers, errcode], "http:" + url)

def episode_find(query, phenny): 
    query = query.replace('!', '')
    if re.compile('(?i)(season \d+(,)? episode \d+)').match(query):
        regex = re.compile('(?i)season (\d+)(?:,)? episode (\d+)')
        numbers = regex.findall(query)
        results = [int(i) for i in numbers[0]]
        snum = str(int(results[0]))
        enum = str(int(results[1]))
        uri = 'http://ponyapi.apps.xeserv.us/season/' + snum + '/episode/' + enum
        nl = query
        issearch = False
        isnextlast = False
    else:
        if re.compile('(?i)((s|se)\d+(, | |,)?(e|ep)\d+)').match(query):
            regex = re.compile('(?i)(?:s|se)(\d+)(?:, | |,)?(?:e|ep)(\d+)')
            numbers = regex.findall(query)
            results = [int(i) for i in numbers[0]]
            snum = str(int(results[0]))
            enum = str(int(results[1]))
            uri = 'http://ponyapi.apps.xeserv.us/season/' + snum + '/episode/' + enum
            nl = query
            issearch = False
            isnextlast = False
        else:
            if re.compile('(?i)next').match(query):
                uri = 'http://ponyapi.apps.xeserv.us/newest'
                nl = 'next'
                issearch = False
                isnextlast = True
            else:
                if re.compile('(?i)last').match(query):
                    uri = 'http://ponyapi.apps.xeserv.us/last_aired'
                    nl = 'last'
                    issearch = False
                    isnextlast = True
                else:
                    if re.compile('(?i)(movie)( )?\d+').match(query):
                        regex = re.compile('(?i)movie(?: )?(\d+)')
                        numbers = regex.findall(query)
                        results = [int(i) for i in numbers[0]]
                        mnum = str(int(results[0]))
                        uri = 'http://ponyapi.apps.xeserv.us/season/99/episode/' + mnum
                        nl = query
                        issearch = False
                        isnextlast = False
                    else:
                        webquery = web.quote(query)
                        uri = 'http://ponyapi.apps.xeserv.us/search?q=' + webquery
                        nl = query
                        issearch = True
                        isnextlast = False
                    
    try:
        rec_bytes = web.get(uri)
    except:
        if isnextlast is True:
            return 'nope$' + nl
        else:
            return
    try:
        jsonstring = json.loads(rec_bytes)
    except:
        return
    try:
        jsonstring['episodes'][0]
    except:
        try:
            jsonstring['episodes']['name']
        except:
            try:
                jsonstring['episode']['name']
            except:
                return 'nope$' + nl
    try:
        epname = jsonstring['episodes'][0]['name']
        eps = str(jsonstring['episodes'][0]['season'])
        epe = str(jsonstring['episodes'][0]['episode'])
        etimeun = jsonstring['episodes'][0]['air_date']
        movie = jsonstring['episodes'][0]['is_movie']
        epnumbered = True
    except:
        try:
            epname = jsonstring['episodes']['name']
            eps = str(jsonstring['episodes']['season'])
            epe = str(jsonstring['episodes']['episode'])
            etimeun = jsonstring['episodes']['air_date']
            movie = jsonstring['episodes']['is_movie']
            epnumbered = False
        except:
            epname = jsonstring['episode']['name']
            eps = str(jsonstring['episode']['season'])
            epe = str(jsonstring['episode']['episode'])
            etimeun = jsonstring['episode']['air_date']
            movie = jsonstring['episode']['is_movie']
            epnumbered = False
    etimegmt = time.gmtime(etimeun)
    etimeus = time.strftime('%A %B %d, %G at %I:%M:%S %p',etimegmt)
    if epnumbered is True and issearch is True:
        try:
            epname2 = jsonstring['episodes'][1]['name']
            eps2 = str(jsonstring['episodes'][1]['season'])
            epe2 = str(jsonstring['episodes'][1]['episode'])
            etimeun2 = jsonstring['episodes'][1]['air_date']
            movie2 = jsonstring['episodes'][1]['is_movie']
            epsecond = True
            etimegmt2 = time.gmtime(etimeun2)
            etimeus2 = time.strftime('%A %B %d, %G at %I:%M:%S %p',etimegmt2)
        except:
            epsecond = False
    else:
        epsecond = False
    if epsecond is True:
        if movie is True:
            if etimeun < time.time():
                return epname + ' aired on ' + etimeus + ' GMT'
            if etimeun > time.time():
                return epname + ' will air on ' + etimeus + ' GMT'
        else:
            if etimeun < time.time():
                return 'Season ' + eps + ', Episode ' + epe + ', ' + epname + ' aired on ' + etimeus + ' GMT and Season ' + eps2 + ', Episode ' + epe2 + ', ' + epname2 + ' aired on ' + etimeus2 + ' GMT'
            if etimeun > time.time():
                return 'Season ' + eps + ', Episode ' + epe + ', ' + epname + ' will air on ' + etimeus + ' GMT and Season ' + eps2 + ', Episode ' + epe2 + ', ' + epname2 + ' will air on ' + etimeus2 + ' GMT'
    else:
        if movie is True:
            if etimeun < time.time():
                return epname + ' aired on ' + etimeus + ' GMT'
            if etimeun > time.time():
                return epname + ' will air on ' + etimeus + ' GMT'
        else:
            if etimeun < time.time():
                return 'Season ' + eps + ', Episode ' + epe + ', ' + epname + ' aired on ' + etimeus + ' GMT'
            if etimeun > time.time():
                return 'Season ' + eps + ', Episode ' + epe + ', ' + epname + ' will air on ' + etimeus + ' GMT'
def episode(phenny, input): 
    """Finds MLP Episodes. Commands can be .ep season 2 episode 1 or .ep s2e1 or .ep return of harmony or .ep next or .ep last or .ep movie 3"""
    query = input.group(2)
    if not query: return phenny.reply('.ep what?')

    uri = episode_find(query, phenny)
    if uri: 
        if uri.startswith('nope'):
            uris = uri.split('$')
            return phenny.say("Sorry " + input.nick + ", I couldn't find the " + uris[1] + " episode.")
        else:
            phenny.say("Here's what I got, " + input.nick + ": " + uri)
            if not hasattr(phenny.bot, 'last_seen_uri'):
                phenny.bot.last_seen_uri = {}
            phenny.bot.last_seen_uri[input.sender] = uri
    else: phenny.say("Sorry " + input.nick + ", I couldn't find any episodes for '%s'." % query)
episode.commands = ['ep','episode']

if __name__ == '__main__': 
    print(__doc__.strip())
