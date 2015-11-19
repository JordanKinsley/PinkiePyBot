#!/usr/bin/env python

from urllib.parse import quote as urlquote
from urllib.parse import quote_plus as urlquoteplus
from urllib.error import HTTPError
import web
import json
from random import choice

def mlfw(phenny, input):
    """.mlfw <query> - My Little Face When: reaction images with ponies!
    Multiple tags should be separated by commas
    """
    q = input.group(2)
    if not q:
        phenny.say(mlfw.__doc__.strip())
        return
    try:
        req = web.get('http://mylittlefacewhen.com/api/v3/face/?tags__all={0}&order_by=-id&format=json'.format(urlquote(q)))
    except (HTTPError, IOError):
        phenny.say("Oopsie, looks like the Internet is broken")
        return
    
    results = json.loads(req)

    if len(results['objects']) <= 0:
        phenny.say('I have no face for that')
        return

    try:
        object = choice(results['objects'])
        link = 'http://mlfw.info/f/{0}/'.format(object['id'])
        image = 'http://mlfw.info{0}'.format(object['image'])
        imgtitle = object['title']
    except AttributeError:
        phenny.say('No face for that')
        return
    
    phenny.say('Here ya go ' + input.nick + ': ' + imgtitle + ' - ' + image)

mlfw.commands = ('mlfw', 'mfw')
