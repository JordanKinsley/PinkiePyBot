'''
reddit.py - Info about reddit links and check on new posts to subreddit(s)
(C) 2015 Jordan T Kinsley (jordan@jordantkinsley.org)
GPLv2 or later

This module supplies new functions for head.py to handle reddit links. 
Additionally, if a config option is present, it will periodically check 
whatever subreddit(s) is defined and post new comments/links to channel
'''

def post_info(uri):
    '''
    IRC formatting codes primer adapted from https://github.com/myano/jenni/wiki/IRC-String-Formatting
    \x01 - Surrounding a message with ACTION, indicates an action
    \x02 - bold
    \x03 - with numbers N,M defines foreground and background text. See below
    \x1D - italic text
    \x1F - underlined text
    \x16 - swap foreground/background colors
    \x0F - clear formatting
    
    IRC colors are a two digit code for (generally) 16 colors. They map like:
    {00: white, 01: black, 02: blue (navy), 03: green, 04: red, 05: brown (maroon), 
        06: purple, 07: orange (olive), 08: yellow, 09: light green (lime), 
        10: teal, 11: light cyan (aqua), 12: light blue (royal), 
        13: pink (light purple/fuchsia), 14: grey, 15: light grey (silver),
        99: transparent}
    Colors are client-dependent and some clients may render the color codes differently.
    The codes must follow the \x03 character immediately, e.g. \x0314,01
        produces grey text on a black background
    '''
    # define a few characters
    upvote = '\x02\x0312↑\x0F'
    downvote = '\x02\0304↓\x0F'
    
    return post_title, short_link, upvotes, downvotes, subreddit, link_domain
