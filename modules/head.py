#!/usr/bin/env python
"""
head.py - Phenny HTTP Metadata Utilities
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re, urllib, urlparse, time
from htmlentitydefs import name2codepoint
import web
from tools import deprecated

def head(phenny, input): 
   """Provide HTTP HEAD information."""
   uri = input.group(2)
   uri = (uri or '').encode('utf-8')
   if ' ' in uri: 
      uri, header = uri.rsplit(' ', 1)
   else: uri, header = uri, None

   if not uri and hasattr(phenny, 'last_seen_uri'): 
      uri = phenny.last_seen_uri

   try: info = web.head(uri)
   except IOError: return phenny.say("Can't connect to %s" % uri)

   if not isinstance(info, list): 
      info = dict(info)
      info['Status'] = '200'
   else: 
      newInfo = dict(info[0])
      newInfo['Status'] = str(info[1])
      info = newInfo

   if header is None: 
      data = []
      if info.has_key('Status'): 
         data.append(info['Status'])
      if info.has_key('content-type'): 
         data.append(info['content-type'].replace('; charset=', ', '))
      if info.has_key('last-modified'): 
         modified = info['last-modified']
         modified = time.strptime(modified, '%a, %d %b %Y %H:%M:%S %Z')
         data.append(time.strftime('%Y-%m-%d %H:%M:%S UTC', modified))
      if info.has_key('content-length'): 
         data.append(info['content-length'] + ' bytes')
      phenny.reply(', '.join(data))
   else: 
      headerlower = header.lower()
      if info.has_key(headerlower): 
         phenny.say(header + ': ' + info.get(headerlower))
      else: 
         msg = 'There was no %s header in the response.' % header
         phenny.say(msg)
head.commands = ['head']
head.example = '.head http://www.w3.org/'

r_title = re.compile(r'(?ims)<title[^>]*>(.*?)</title\s*>')
r_entity = re.compile(r'&[A-Za-z0-9#]+;')

@deprecated
def f_title(self, origin, match, args): 
   """.title <URI> - Return the title of URI."""
   uri = match.group(2)
   uri = (uri or '').encode('utf-8')

   if not uri and hasattr(self, 'last_seen_uri'): 
      uri = self.last_seen_uri

   if not ':' in uri: 
      uri = 'http://' + uri

   try: 
      redirects = 0
      while True: 
         info = web.head(uri)

         if not isinstance(info, list): 
            status = '200'
         else: 
            status = str(info[1])
            info = info[0]
         if status.startswith('3'): 
            uri = urlparse.urljoin(uri, info['Location'])
         else: break

         redirects += 1
         if redirects >= 25: 
            self.msg(origin.sender, origin.nick + ": Too many redirects")
            return

      try: mtype = info['content-type']
      except: 
         err = ": Couldn't get the Content-Type, sorry"
         return self.msg(origin.sender, origin.nick + err)
      if not (('/html' in mtype) or ('/xhtml' in mtype)): 
         self.msg(origin.sender, origin.nick + ": Document isn't HTML")
         return

      u = urllib.urlopen(uri)
      bytes = u.read(32768)
      u.close()

   except IOError: 
      self.msg(origin.sender, "Can't connect to %s" % uri)
      return

   m = r_title.search(bytes)
   if m: 
      title = m.group(1)
      title = title.strip()
      title = title.replace('\t', ' ')
      title = title.replace('\r', ' ')
      title = title.replace('\n', ' ')
      while '  ' in title: 
         title = title.replace('  ', ' ')
      if len(title) > 200: 
         title = title[:200] + '[...]'
      
      def e(m): 
         entity = m.group(0)
         if entity.startswith('&#x'): 
            cp = int(entity[3:-1], 16)
            return unichr(cp).encode('utf-8')
         elif entity.startswith('&#'): 
            cp = int(entity[2:-1])
            return unichr(cp).encode('utf-8')
         else: 
            char = name2codepoint[entity[1:-1]]
            return unichr(char).encode('utf-8')
      title = r_entity.sub(e, title)

      if not title: 
         title = '[Title is the empty document, "".]'
      self.msg(origin.sender, origin.nick + ': ' + title)
   else: self.msg(origin.sender, origin.nick + ': No title found')
f_title.commands = ['title']

def noteuri(phenny, input): 
   uri = input.group(1).encode('utf-8')
   phenny.bot.last_seen_uri = uri
noteuri.rule = r'.*(http://[^<> "]+)[,.]?'
noteuri.priority = 'low'

if __name__ == '__main__': 
   print __doc__
