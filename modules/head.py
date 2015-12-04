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
import ast
import calendar
import string

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

        youtube = re.compile('http(s)?://((www|m).)?youtube.(com|co.uk|ca)?/watch.*\?.*v\=(.*)')
        if youtube.match(uri) or re.compile('http(s)?://youtu.be/(.*)').match(uri):
            # due to changes in how Youtube gives out API access, we need a key from the config file
            if get_youtube_title(uri, phenny.config.youtube_api_key) is None:
                phenny.say("Sorry " + input.nick + " but you need to fix your URL.")
                return
            else:
                title = get_youtube_title(uri, phenny.config.youtube_api_key)
                istags = False

        fimfiction = re.compile('http(s)?://(www.)?fimfiction.net/story/')
        if fimfiction.match(uri):
            title = get_story_title(uri)
            istags = False

        if re.compile('http(s)?://(www.)?((e621)|(e926)).net/post/show/').match(uri): #e621 or e926 link
            title = ouroboros('e621',uri, phenny)
            istags = True
        
        if re.compile('http(s)?://(.+)?deviantart.com/art/').match(uri):
            title = deviantart(uri, phenny)
            istags = False
        
        if re.compile('http(s)?://(.+)?deviantart.com/journal/').match(uri):
            title = deviantart(uri, phenny)
            istags = False
        
        if re.compile('http(s)?://fav.me/').match(uri):
            title = deviantart(uri, phenny)
            istags = False
        
        if re.compile('http(s)?://sta.sh/').match(uri):
            title = deviantart(uri, phenny)
            istags = False
        
        if re.compile('http(s)?://(.+)?deviantart.com/(.+)/d').match(uri):
            title = deviantart(uri, phenny)
            istags = False

        if re.compile('http(s)?://(www.)?twentypercentcooler.net/post/show/').match(uri):
            title = ouroboros('twentypercentcooler',uri, phenny)
            istags = True

        if re.compile('http(s)?://(www.)?derpiboo((.ru)|(ru.org))(/images)?/').match(uri):
            title = derpibooru(uri, phenny)
            istags = True

        if title:
            if istags is True:
                phenny.say('[ ' + title + ' ]')
            else:
                phenny.say('[ ' + title + ' ]')
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

def query(vid, auth_key):
    ''' 
    returns the title, viewcount, time, and uploader of a Youtube video. 
    vid is the Youtube video ID at the end of the Youtube URL.
    '''
    
    main = 'https://www.googleapis.com/youtube/v3/videos?id='
    key = '&key=' + auth_key
    ext = '&part=snippet,contentDetails,statistics'
    
    req = web.get(main + vid + key + ext)
    data = json.loads(req, encoding='utf-8')
    try:
        data = data['items'][0]
    except IndexError: return None
    title = data['snippet']['title']
    uploader = data['snippet']['channelTitle']
    try:
        viewcount = str(data['statistics']['viewCount'])
    except (KeyError, IndexError):
        viewcount = '0'
    duration = str(data['contentDetails']['duration'])
    # a video with no likes results in IndexErrors (assuming true for ratingCount, too)
    try:
        likes = str(data['statistics']['likeCount'])
    except (KeyError, IndexError):
        likes = '0'
    try:
        dislikes = str(data['statistics']['dislikeCount'])
    except (KeyError, IndexError):
        dislikes = '0'
    
    time = iso_8601(duration)
    
    return title, viewcount, time, uploader, likes, dislikes
    
def iso_8601(str_time):
    '''
    Google's Youtube data V3 API gives duration in an ISO 8601 format, e.g.
    P3DT4H30M44S. Each format of time, i.e. 3D, 4H, 30M, 44S are optional 
    in the string. P1D is just as valid as PT24H, for instance (and is the
    actual value returned for a video exactly 24 hours, 0 minutes, and 
    0 seconds long)
    
    returns a string of the time, formatted like 3d 4h 30m 44s
    '''
    
    iso_8601_re = re.compile('P(?P<year>[0-9]*Y)?(?P<month>[0-9]*M)?(?P<week>[0-9]*W)?(?P<day>[0-9]*D)?(T)?(?P<hour>[0-9]*H)?(?P<minute>[0-9]*M)?(?P<second>[0-9]*S)?')
    
    found_time = re.match(iso_8601_re, str_time)
    year, month, week, day, hour, minute, second = '','','','','','',''
    return_time = ''
    if found_time.group('year'):
        year = found_time.group('year').rstrip('Y')
        return_time = return_time + year + 'y '
    if found_time.group('month'):
        month = found_time.group('month').rstrip('M')
        return_time = return_time + month + 'm '
    if found_time.group('week'):
        week = found_time.group('week').rstrip('W')
        return_time = return_time + week + 'w '
    if found_time.group('day'):
        day = found_time.group('day').rstrip('D')
        return_time = return_time + day + 'd '
    if found_time.group('hour'):
        hour = found_time.group('hour').rstrip('H')
        return_time = return_time + hour + 'h '
    if found_time.group('minute'):
        minute = found_time.group('minute').rstrip('M')
        return_time = return_time + minute + 'm '
    if found_time.group('second'):
        second = found_time.group('second').rstrip('S')
        return_time = return_time + second + 's '
    return return_time

def get_youtube_title(uri, auth_key):
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

    title, views, time, uploader, likes, dislikes = query(vid, auth_key)
    if title == '':
        return None
    percentage = get_percentage(likes, dislikes)
    # Not including the uploader in the title info; it's rarely important in determining a link's quality.
    return title + " - " + views + " views - " + time + "long - " + likes + " likes - " + percentage + "%"

def get_api_story_title(uri):
    story_id = uri.split('story/')[1]
    if story_id.find('/') > 1:
        story_id = story_id.split('/')[0]
    data = web.get('http://fimfiction.net/api/story.php?story=' + story_id)
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

def smart_truncate(content, phenny):
    try:
        if phenny.config.tag_list_length:
            suffix=' ...'
            try:
                length=int(phenny.config.tag_list_length)
            except:
                return "The tag_list_length option is not set correctly, please fix it"
            if len(content) <= length:
                return content
            else:
                return content[:length].rsplit(' ', 1)[0]+suffix
    except:
        return "Please set the tag_list_length option in the config"

def ouroboros(site, uri, phenny):
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
    content = filtered
    filtered = smart_truncate(content, phenny)
    title = re.sub('_',"_",filtered)
    title = '{0} {1}'.format(rating.capitalize(),title)
    return title

def derpibooru(uri, phenny):
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
    content = title
    title = smart_truncate(content, phenny)
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

def deviantart(uri, phenny):
    apiuri = 'http://backend.deviantart.com/oembed?url=' + web.quote(uri)
    try:
        rec_bytes = web.get(apiuri)
    except:
        return
    try:
        jsonstring = json.loads(rec_bytes)
    except:
        return
    type = jsonstring['type']
    title = jsonstring['title']
    category = jsonstring['category']
    author = jsonstring['author_name']
    safe = jsonstring['safety']
    uploaded = jsonstring['pubdate']
    views = str(jsonstring['community']['statistics']['_attributes']['views'])
    favs = str(jsonstring['community']['statistics']['_attributes']['favorites'])
    try:
        import dateutil.parser
        isdateutil = True
        dt = dateutil.parser.parse(uploaded)
        timestamp1 = calendar.timegm(dt.timetuple())
        timestamp1 = time.gmtime(timestamp1)
        uploadedformat = time.strftime('%A %B %d, %G at %I:%M:%S %p',timestamp1)
    except:
        isdateutil = False
    if re.compile('nonadult').match(safe):
        nsfw = False
    else:
        nsfw = True
    if nsfw is True:
        if isdateutil is True:
            return '\002!!NSFW!!\017 DeviantArt ' + title + ' by ' + author + ' - ' + category + ' - ' + type + ' uploaded on ' + uploadedformat + ' - ' + views + ' views - ' + favs + ' favs'
        else:
            return '\002!!NSFW!!\017 DeviantArt ' + title + ' by ' + author + ' - ' + category + ' - ' + type + ' - ' + views + ' views - ' + favs + ' favs'
    else:
        if isdateutil is True:
            return 'DeviantArt ' + title + ' by ' + author + ' - ' + category + ' - ' + type + ' uploaded on ' + uploadedformat + ' - ' + views + ' views - ' + favs + ' favs'
        else:
            return 'DeviantArt ' + title + ' by ' + author + ' - ' + category + ' - ' + type + ' - ' + views + ' views - ' + favs + ' favs'

if __name__ == '__main__': 
    print(__doc__.strip())
