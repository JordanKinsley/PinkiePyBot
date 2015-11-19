#!/usr/bin/env python
"""
web.py - Web Facilities
Author: Sean B. Palmer, inamidst.com
About: http://inamidst.com/phenny/
"""

import re, urllib.request, urllib.parse, urllib.error
from html.entities import name2codepoint
import json as jsonlib

class Grab(urllib.request.URLopener): 
    def __init__(self, *args): 
        self.version = 'Mozilla/5.0 (CompuBot)'
        urllib.request.URLopener.__init__(self, *args)
    def http_error_default(self, url, fp, errcode, errmsg, headers): 
        return urllib.addinfourl(fp, [headers, errcode], "http:" + url)
urllib.request._urlopener = Grab()

def get(uri): 
    if not uri.startswith('http'): 
        return
    '''try:
    	u = urllib.request.urlopen(uri)
    except urllib.error.HTTPError:'''
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    u = opener.open(uri)
    bytes = u.read()
    try:
        bytes = bytes.decode('utf-8')
    except UnicodeDecodeError:
        bytes = bytes.decode('ISO-8859-1')
    u.close()
    return bytes

def head(uri): 
    if not uri.startswith('http'): 
        return
    u = urllib.request.urlopen(uri)
    info = u.info()
    u.close()
    return info

def post(uri, query): 
    if not uri.startswith('http'): 
        return
    data = urllib.parse.urlencode(query).encode('utf-8')
    u = urllib.request.urlopen(uri, data)
    bytes = u.read()
    try:
        bytes = bytes.decode('utf-8')
    except UnicodeDecodeError:
        bytes = bytes.decode('ISO-8859-1')
    u.close()
    return bytes

r_entity = re.compile(r'&([^;\s]+);')

def entity(match): 
    value = match.group(1).lower()
    if value.startswith('#x'): 
        return chr(int(value[2:], 16))
    elif value.startswith('#'): 
        return chr(int(value[1:]))
    elif value in name2codepoint: 
        return chr(name2codepoint[value])
    return '[' + value + ']'

def quote(text):
     return urllib.parse.quote(text)

def decode(html): 
    return r_entity.sub(entity, html)

def unquote(text):
     return urllib.parse.unquote(text)

r_string = re.compile(r'("(\\.|[^"\\])*")')
r_json = re.compile(r'^[,:{}\[\]0-9.\-+Eaeflnr-u \n\r\t]+$')
env = {'__builtins__': None, 'null': None, 'true': True, 'false': False}

def json(text): 
    """Evaluate JSON text safely (we hope)."""
    return jsonlib.loads(text)

if __name__=="__main__": 
    main()
