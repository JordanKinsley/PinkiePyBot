#!/usr/bin/env python
'''
head.py - Phenny HTTP Metadata Utilities
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/

Modified by Jordan Kinsley <jordan@jordantkinsley.org>
'''

import re, os.path, json, imp
import urllib.request
import urllib.parse
import urllib.error
import http.client
import http.cookiejar
import time
from datetime import timedelta
from html.entities import name2codepoint
import web
from tools import deprecated
try: 
    import reddit
except: 
    pass

cj = http.cookiejar.LWPCookieJar(os.path.join(os.path.expanduser('~/.phenny'), 'cookies.lwp'))
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
urllib.request.install_opener(opener)

def head(phenny, input): 
    """Provide HTTP HEAD information."""
    uri = input.group(2)
    uri = (uri or '')
    if ' ' in uri: 
        uri, header = uri.rsplit(' ', 1)
    else: uri, header = uri, None

    if not uri and hasattr(phenny, 'last_seen_uri'): 
        try: uri = phenny.last_seen_uri[input.sender]
        except KeyError: return phenny.say('?')

    if not uri.startswith('htt'): 
        uri = 'http://' + uri
    # uri = uri.replace('#!', '?_escaped_fragment_=')
    
    start = time.time()

    try:
        info = web.head(uri)
        info['status'] = '200'
    except urllib.error.HTTPError as e:
        return phenny.say(str(e.code))
    except http.client.InvalidURL:
        return phenny.say("Not a valid URI, sorry.")
    except IOError:
        return phenny.say("Can't connect to %s" % uri)

    resptime = time.time() - start

    if header is None: 
        data = []
        if 'Status' in info: 
            data.append(info['Status'])
        if 'content-type' in info: 
            data.append(info['content-type'].replace('; charset=', ', '))
        if 'last-modified' in info: 
            modified = info['last-modified']
            modified = time.strptime(modified, '%a, %d %b %Y %H:%M:%S %Z')
            data.append(time.strftime('%Y-%m-%d %H:%M:%S UTC', modified))
        if 'content-length' in info: 
            data.append(info['content-length'] + ' bytes')
        data.append('{0:1.2f} s'.format(resptime))
        phenny.reply(', '.join(data))
    else: 
        headerlower = header.lower()
        if headerlower in info: 
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
    uri = (uri or '')

    if not uri and hasattr(self, 'last_seen_uri'): 
        uri = self.last_seen_uri.get(origin.sender)
    if not uri: 
        return self.msg(origin.sender, 'I need a URI to give the title of...')
    title = gettitle(uri)
    if title:
        self.msg(origin.sender, origin.nick + ': ' + title)
    else: self.msg(origin.sender, origin.nick + ': No title found')
f_title.commands = ['title']

def noteuri(phenny, input): 
    uri = input.group(1)
    if not hasattr(phenny.bot, 'last_seen_uri'): 
        phenny.bot.last_seen_uri = {}
    phenny.bot.last_seen_uri[input.sender] = uri
noteuri.rule = r'.*(http[s]?://[^<> "\x01]+)[,.]?'
noteuri.priority = 'low'

titlecommands = r'(?:' + r'|'.join(f_title.commands) + r')'
def snarfuri(phenny, input):
    if re.match(r'(?i)' + phenny.config.prefix + titlecommands, input.group()):
        return
    uri = input.group(1)
    if input.nick in ('derpy','Chance'):
        return
    try:
        if re.compile('http(s)?://(.*).(jpg|jpeg|png|gif|tiff|bmp)').match(uri):
            return None
        
        title = None

        youtube = re.compile('http(s)?://(www.)?youtube.(com|co.uk|ca)?/watch(.*)\?v(.*)')
        if youtube.match(uri) or re.compile('http(s)?://youtu.be/(.*)').match(uri):
            title = get_youtube_title(uri)

        fimfiction = re.compile('http(s)?://(www.)?fimfiction.net/story/')
        if fimfiction.match(uri):
            title = get_story_title(uri)

        if re.compile('http(s)?://(www.)?((e621)|(e926)).net/post/show/').match(uri): #e621 or e926 link
            title = ouroboros('e621',uri)

        if re.compile('http(s)?://(www.)?twentypercentcooler.net/post/show/').match(uri):
            title = ouroboros('twentypercentcooler',uri)

        if re.compile('http(s)?://(www.)?derpiboo((.ru)|(ru.org))(/images)?/').match(uri):
            title = derpibooru(uri)

        if re.compile('http(s)?://(www.)?redd(.it|it.com)/').match(uri):
            title = reddit_post(uri)
        if title:
            phenny.msg(input.sender, '[ ' + title + ' ]')
        else:
            title = gettitle(uri)
            if title: phenny.msg(input.sender, '[ ' + title + ' ]')
    except http.client.HTTPException:
        return
snarfuri.rule = r'.*(http[s]?://[^<> "\x01]+)[,.]?'
snarfuri.priority = 'low'

def gettitle(uri):
    if not ':' in uri: 
        uri = 'http://' + uri
    uri = uri.replace('#!', '?_escaped_fragment_=')

    title = None
    localhost = [
        'http://localhost/', 'http://localhost:80/', 
        'http://localhost:8080/', 'http://127.0.0.1/', 
        'http://127.0.0.1:80/', 'http://127.0.0.1:8080/', 
        'https://localhost/', 'https://localhost:80/', 
        'https://localhost:8080/', 'https://127.0.0.1/', 
        'https://127.0.0.1:80/', 'https://127.0.0.1:8080/', 
    ]
    for s in localhost: 
        if uri.startswith(s): 
            return

    if re.compile('http(s)?://(www.)?bad-dragon.com/').match(uri) and not check_cookie('baddragon_age_checked'):
        urllib.request.urlopen('http://bad-dragon.com/agecheck/accept')

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
                uri = urllib.parse.urljoin(uri, info['Location'])
            else: break

            redirects += 1
            if redirects >= 25: 
                return None

        try: mtype = info['content-type']
        except: 
            return None

        try:
            # Occasionally throws type errors if a CSS file is given. 
            if not (('/html' in mtype) or ('/xhtml' in mtype)): 
                return None
        except:
            return None

        bytes = web.get(uri)
        #bytes = u.read(262144)
        #u.close()

    except IOError: 
        return
    except UnicodeError:
        '''
        Due to the way Python implemented the urllib.request.urlopen() 
        function, it is not possible to correct for Unicode characters
        like € in a URL. Therefore, we just catch the error and don't
        provide a title for the link. Other options may be worth 
        exploring, and could be included here. 
        '''
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
                return chr(cp)
            elif entity.startswith('&#'): 
                cp = int(entity[2:-1])
                return chr(cp)
            else: 
                char = name2codepoint[entity[1:-1]]
                return chr(char)
        title = r_entity.sub(e, title)

        if title: 
            title = title.replace('\n', '')
            title = title.replace('\r', '')
        else: title = None
    return title

def check_cookie(name):
    ''' checks the given name against the names of cookies in the cookie
    jar; returns true iff it finds an exact match.'''
    for cookie in cj:
        if cookie.name == name:
            return True
        else: continue
    return False

def query(vid):
    ''' returns the title, viewcount, time, and uploader of a Youtube video. vid is the Youtube video ID at the end of the Youtube URL.'''
    main = 'http://gdata.youtube.com/feeds/api/videos/'
    ext = '?v=2&alt=jsonc'
    try:
        req = web.get(main + vid + ext)
    except (urllib.error.HTTPError, IOError):
        return '', '', '', '', '', ''
    data = json.loads(req, encoding='utf-8')
    data = data['data']
    
    title = data['title']
    uploader = data['uploader']
    try:
        viewcount = str(data['viewCount'])
    except (KeyError, IndexError):
        viewcount = '0'
    duration = str(data['duration'])
    # a video with no likes results in IndexErrors (assuming true for ratingCount, too)
    try:
        likes = str(data['likeCount'])
    except (KeyError, IndexError):
        likes = '0'
    try:
        ratings = str(data['ratingCount'])
    except (KeyError, IndexError):
        ratings = '0'
    time = str(timedelta(seconds=int(duration)))
    return title, viewcount, time, uploader, likes, ratings

def get_youtube_title(uri):
    vid = None
    if 'youtu.be/' not in uri:
        if '?v=' in uri:
            vid = uri[uri.index('?v=')+3:uri.index('?v=') + 14]
        elif '&v=' in uri:
            vid = uri[uri.index('&v=')+3:uri.index('&v=') + 14]
        else:
            return None
    else:
        vid = uri[uri.rindex('be/')+3:uri.rindex('be/')+14]

    title, views, time, uploader, likes, ratings = query(vid)
    if title == '':
        return None
    if int(ratings) > 0:
        percentage = str(round((float(likes) / float(ratings)) * 100,2))
    else:
        percentage = '0.00'
    # Not including the uploader in the title info; it's rarely important in determining a link's quality.
    return title + " - " + views + " views - " + time + " long - " + likes + " likes - " + percentage + "%"

def get_api_story_title(uri):
    story_id = uri.split('story/')[1]
    if story_id.find('/') > 1:
        story_id = story_id.split('/')[0]
    data = urllib.request.urlopen('http://fimfiction.net/api/story.php?story=' + story_id).read().decode()
    story = json.loads(data, encoding='utf-8')['story']
    
    story_title = format_title(story['title'])
    likes = str(story['likes'])
    dislikes = str(story['dislikes'])
    percentage = get_percentage(likes, dislikes)
    author = story['author']['name'].strip('"')
    views = str(story['views'])
    words = str(story['words'])
    content_rating = int(story['content_rating'])
    chapters = str(story['chapter_count'])
    categories = ''
    
    cat_dict = story['categories']
    for k in cat_dict:
        if cat_dict[k] is True:
            categories = categories + '[' + k + ']'
    return story_title, likes, dislikes, percentage, author, views, words, content_rating, chapters, categories
    
def format_title(title):
    title = title.strip('"')
    title = title.replace('&#039;','\'')
    title = title.replace('&amp;','&')
    title = title.replace('&quot;','"')
    title = title.replace('&lt;','<')
    title = title.replace('&gt;','>')
    return title
    
def get_percentage(likes, dislikes):
    percentage = ''
    if int(likes) > 0 or int(dislikes) > 0:
        percentage = (float(likes) / (float(dislikes) + float(likes))) * 100
        percentage = str(round(percentage, 2))
    else:
        # no likes and dislikes
        percentage = '0.00'
    return percentage

def ouroboros(site, uri):
    # e621 and twentypercentcooler use the same software
    # TODO: load tag file; compare tags, generate title
    #load a list of unimportant tags from a file. possible regex?
    title = ''
    def get_id(link):
        exp = '(.*)show/(?P<id>[0-9]*)/?'
        return re.search(exp, link).group('id')
    post_id = get_id(uri)
    json_data = web.get('https://{0}.net/post/show.json?id={1}'.format(site, post_id))
    postdata = json.loads(json_data, encoding='utf-8')
    tags = postdata['tags']

    ratings = { 's' : 'Safe', 'q' : 'Questionable', 'e' : 'Explicit' }
    if postdata['rating'] in ratings:
        rating = ratings[postdata['rating']]
    else:
        rating = 'Unknown'
    #compare tags to a list of uniportant tags and drop some/most
    tag_file = os.path.expanduser('~/.phenny/boru.py')
    try:
        boru = imp.load_source('boru',tag_file)
    except Exception as e:
        print("Error loading ignore tags: {0} (in head.py)".format(e))
        filtered = tags
    else:
        filtered = re.sub("\\b(("+")|(".join(boru.ignore_tags)+"))\\b","",tags)
        filtered = re.sub(" +"," ",filtered).strip()
    title = re.sub('_'," ",filtered)
    title = '{0} {1}'.format(rating.capitalize(),title)
    return title

def derpibooru(uri):
    # TODO: research derpibooru's API and get data
    def get_id(link):
        exp = '(.*)derpiboo((.ru)|(ru.org))(/images)?/(?P<id>[0-9]*)/?'
        return re.search(exp, link).group('id')
    id = get_id(uri)
    if not id:
        return gettitle(uri)
    json_data = web.get('http://derpiboo.ru/{0}.json'.format(id))
    postdata = json.loads(json_data, encoding='utf-8')
    tags = postdata['tags'].split(', ')
    
    artists = []
    for tag in tags:
        if tag.startswith('artist:'):
            artists.append(tag.replace('artist:', '', 1))
    if artists:
        artists = ' by '+', '.join(artists)
    else:
        artists = ''
    # ratings are tags on Derpibooru
    ratings = []
    for tag in tags:
        if tag in {'explicit', 'grimdark', 'grotesque', 'questionable', 'safe', 'semi-grimdark', 'suggestive'}:
            ratings.append(tag)
    if not ratings:
        ratings = ['unknown']
    ratings = ' '.join(ratings)
    tag_file = os.path.expanduser('~/.phenny/boru.py')
    try:
        boru = imp.load_source('boru',tag_file)
    except Exception as e:
        print("Error loading ignore tags: %s (in head.py)" %(e))
    else:
        tags = [tag for tag in tags if tag not in boru.ignore_tags]
    tag_string = ' '.join(tag.replace(' ', '_') for tag in tags)
    title = '{0} {1}'.format(ratings.title(),tag_string,artists)
    return title

def get_story_title(uri):
    story_title, likes, dislikes, percentage, author, views, words, content_rating, chapters, categories = get_api_story_title(uri)
    title = ''
    if content_rating > 1:
        title = title + '\u0002!!*NSFW*!!\u000F - '
    title = title + story_title + " by " + author
    if chapters:
        title = title + ' - ' + str(chapters)
        if int(chapters) > 1:
            title = title + ' chapters'
        else:
            title = title + ' chapter'
    title = title + " - " + views + " views - " + categories + ' - ' + words + ' words'
    title = title + " - Likes: " + likes + " - Dislikes: " + dislikes + " - " + percentage + "%"
    return title

def reddit_post(uri):
    # initial commit
    if reddit:
        post_title, short_link, upvotes, downvotes, subreddit, link_domain = reddit.post_info(uri)
        title = subreddit + ': ' + post_title + ' (' + link_domain + ') ' + upvotes + downvotes + ' (' + short_link ')'
    else:
        title = gettitle(uri)
    return title

if __name__ == '__main__': 
    print(__doc__.strip())
