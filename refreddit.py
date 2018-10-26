# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 20:05:11 2017

@author: colditzjb
"""
import os, datetime, time

import praw #PRAW is not a standard library, so install it first 

### Raven is a Sentry implementation that broadcasts errors to other platforms (e.g., Slack channel)
#from raven import Client
#r_client = Client(
#    # This is the secret key
#    dsn = 'SECRET KEY HERE (THIS IS AN URL)',
#
#    # This will appear as the host name in alerts
#    name='HOSTNAME HERE',
#        
#    ignore_exceptions = [
#            'Http404',
#            'django.exceptions.*',
#            TypeError,
#            ValueError,
#            ]
#    )

dir_data = './data/reddit_stream/' # Include the trailing slash!

reddit = praw.Reddit(client_id='USE YOUR REDDIT API CREDS HERE',
                     client_secret='USE YOUR REDDIT API CREDS HERE',
                     password='USE YOUR REDDIT API CREDS HERE',
                     user_agent='USE YOUR REDDIT API CREDS HERE',
                     username='USE YOUR REDDIT API CREDS HERE')

#print(reddit.user.me()) #Check that the Reddit API is set up and connected properly


sublist = ['pics', 'lolcats', 'eli5'] # UPDATE THIS TO INCLUDE SUBREDDITS THAT YOU WANT TO FOLLOW


"""
ERROR AND PROCESS LOGGING:
    log_level (integer: between 0 and 9)
        9: logs all process checkpoints for tracking and debugging
        8: datalines
        7: post metadata
        6: history status (e.g., content removed)
        5: file added/appended
        4: 
        3: errors related to non-existent or inaccessible subreddits
        2: PRAWblematic errors ### TO-DO in __main__ (not implemented)
        1: unanticipated script errors
        0: ignoring all errors
        
    debug (boolean)
        If True, this prints log output to to the console screen
        
    outfile (None or file name as a string)
        If defined, this outputs a log to the defined file
""" 
log_level = 2
debug = False
log_out = 'log.txt' 

def log(text, level=9, log_level=log_level, debug=debug, outfile=log_out, sentry=False):
    if level<=log_level:
        if debug:
            print(str(text)+'\n')
        if outfile:
            with open(dir_data+outfile,'a+') as bugfile:
                bugfile.write(str(text)+'\n')
        if sentry:
            r_client.captureMessage('Error: '+str(text))
    else:
        pass

"""
Creates a new directory, if it doesn't already exist
Returns the full directory path as a string
"""
def mk_dir(dir_data=dir_data, dir_sub=None, dir_date=None, 
           dir_post=None, dir_comm=None):
    dir_listing = [dir_data[:-1], dir_sub, dir_date, dir_post, dir_comm]
    dir_reduced = [x for x in dir_listing if x is not None]
    mk = ('/'.join(dir_reduced))+'/'
    log('--- Checkmate directory: '+mk)
    os.makedirs(mk, exist_ok=True)
    return mk


def history_read(dir_target):
    i = 0
    with open(dir_target+'history.csv', 'r') as history:
        for line in history:
            elements = line.split(',')
            ts = elements[0]
            coms = elements[2]
            if len(elements[3]) > 0:
                updated = elements[3]
            else: 
                updated = 0
            i = i+1
    return {'entries':i, 
            'lastime':ts,
            'updated':updated,
            'comments':coms}



"""
HOW POSTS ARE RETRIEVED:
    post_limit (integer)
        Up to 1000, but every 100 requires a separate API call
"""
post_limit=1000
def getposts(sub, limit=post_limit):
    log('Getting posts...')
    i=0
    postData = reddit.subreddit(sub).new(limit=limit)
    try:
        for post in postData:
            date = datetime.datetime.fromtimestamp(post.created_utc).strftime('%Y%m%d')
            mk = mk_dir(dir_sub=sub, dir_date=date, dir_post=post.id)
            i = i+1
            log('Post #'+str(i)+' \t'+sub+'\t'+date+'\t'+post.id, level=7)
            metadata(mk, post, obj_type='post')
            
    except Exception as e:
        log(str(e), level=1)
        #log('"'+sub+'" is inaccessible or has no available posts.', level=3)

def getpost(dir_target, obj, edited):
    log('  Getting post...')
    
    try:
        with open(dir_target+str(edited)+'.txt', 'w+') as outfile:
            outfile.write(obj.title+'\n\n'+obj.selftext)
        log(dir_target+str(edited)+'.txt added',level=5)
    except Exception as e:
        log(str(e), level=1)
        pass


"""
"""
max_cycle = 200
refresh_delay = 1*24*60*60 
retire_delay = 30*24*60*60 #Reddit retires activity after 180 days
def refreshposts(sub, max_cycle=max_cycle, delay=refresh_delay, retired=retire_delay):

    utc_now = datetime.datetime.utcnow()
    ts = int(utc_now.timestamp())
    
    i=0

    try:
        datefolders = sorted(os.listdir(dir_data+sub+'/'), reverse=True)
        to_get = []
        for date in datefolders:
            datestamp = int(datetime.datetime.strptime(date,'%Y%m%d').timestamp())
            if datestamp > ts - retired:
                to_get.append(date)
        log(str(to_get))
    
        for dir_date in to_get:
            dir_search = dir_data+sub+'/'+dir_date+'/'
            for dir_file in sorted(os.listdir(dir_search), reverse=True):
                if '.' not in dir_file:
                    dir_target = dir_data+sub+'/'+dir_date+'/'+dir_file+'/'
                    history = history_read(dir_target)
                    if (
                        int(history['lastime']) < ts - delay and 
                        int(history['updated']) < 9999999990 and 
                        i < max_cycle
                        ):
                        post = reddit.submission(id=dir_file)
                        metadata(dir_target, post, 'post', delay=delay)
                        i = i+1
    except Exception as e:
        log('refreshposts() returned '+str(e), level=2)

"""
HOW COMMENTS ARE RETRIEVED
"""
def getcomments(dir_target, post, edited):
    log('  Getting comments...')
    post.comments.replace_more(limit=None)
    i=0
    for comment in post.comments.list():
        #comment.body
        #comment.parent_id
        parent=comment.parent_id.split('_')[1]
        if parent == post.id:
            dircomm = comment.id
        else:
            dircomm= comment.id+'-'+parent
    
        i=i+1
        sub = str(post.subreddit)
        date = datetime.datetime.fromtimestamp(post.created_utc).strftime('%Y%m%d')
        mk = mk_dir(dir_data=dir_target, dir_comm=dircomm)
        log('Comm #'+str(i)+' \t'+sub+'\t'+date+'\t'+post.id, level=7)
        metadata(mk, comment, obj_type='comment')


def getcomment(dir_target, obj, edited):
    log('  Getting comment...')
    try:
        with open(dir_target+str(edited)+'.txt', 'w+') as outfile:
            outfile.write(obj.body)
        log(dir_target+str(edited)+'.txt added',level=5)
    except Exception as e:
        log(str(e), level=1)




"""
HANDLES OBJECT METADATA AND UPDATES HISTORY FILES
    delay (integer)
        How many seconds to wait before saving a new history checkpoint
            1 hour = 3600 seconds; 1 day = 86400 seconds
        Note: new or updated content will be given priority
"""
delay = 2*60*60
def metadata(dir_target, obj, obj_type, delay=delay):

    utc_now = datetime.datetime.utcnow()
    ts = int(utc_now.timestamp())

    created = int(obj.created_utc)
    edited = int(obj.edited)
    if edited == 0:
        edited = created

    if obj_type == 'post':
        if obj.selftext == '[removed]':
            edited = 9999999998
        elif obj.selftext == '[deleted]':
            edited = 9999999999
    elif obj_type == 'comment':
        if obj.body == '[removed]':
            edited = 9999999998
        elif obj.body == '[deleted]':
            edited = 9999999999


    author = str(obj.author)
    score = int(obj.score)
    if obj_type=='post':
        comments = int(obj.num_comments)
    else:
        comments = ''
        
    try: days = int(obj.author_flair_text.split(' ')[0])
    except: days = ''
    

    def getit(dir_target=dir_target,obj=obj, obj_type=obj_type, edited=edited):
        if obj_type == 'post':
            log('Running getpost()')
            getpost(dir_target, obj, edited)
        elif obj_type == 'comments':
            log('Running getcomments()')
            getcomments(dir_target, obj, edited)
        elif obj_type == 'comment':
            log('Running getcomment()')
            getcomment(dir_target, obj, edited)
        else:
            pass
    
    def history_out(i=ts, s=score, c=comments, t=edited, d=days, a=author):
        dataline = ','.join([str(i), str(s), str(c), str(t), str(d), str(a)])
        log(' Data: '+dataline, level=8)
        with open(dir_target+'history.csv', 'a+') as history:
            history.write(dataline+'\n')
        log(dir_target+'history.csv appended',level=5)

                
    if 'history.csv' not in os.listdir(dir_target):
        log('History: new '+obj_type,level=6)
        getit()
        if obj_type=='post': 
                getit(obj_type='comments')
        history_out()
        written = True
    else:
        com_count=history_read(dir_target)['comments']
        updated=history_read(dir_target)['updated']
        lastime=history_read(dir_target)['lastime']
        if edited > created: #check for update if post was ever edited
            if edited > 9999999990:
                log(' History: content removed',level=6)
                #if int(updated) < edited:   ### Something wonky going on here...
                #    history_out(t=edited, a='')
                #    written = True
                #else: written = False
                written = True ### Here's the work around
            elif int(updated) < edited:
                log(' History: content edited',level=6)
                getit()
                history_out(a='')
                written = True
            elif int(lastime) <= ts - delay:
                log(' History: checkpoint added',level=6)
                history_out(t='',a='')
                written = True
            else:
                log(' History: checkpoint skipped',level=6)
                written = False
        elif int(lastime) <= ts - delay:
            log(' History: checkpoint added',level=6)
            history_out(t='',a='')
            written = True
        else:
            log(' History: checkpoint skipped',level=6)
            written = False
            #check edit and getpost()
        if obj_type=='post':
            if comments > int(com_count):
                log(' History: new comments',level=6)
                getit(obj_type='comments')
                if not written: 
                    history_out(t='',a='')
                    written = True
    return written





"""
This is the final function, to cycle through 
"""
timeout = 5*60
def cycle(subs=sublist, timeout=timeout):
    # Need to update this! Don't sleep per subreddit!
    while True:
        utc_now = datetime.datetime.utcnow()
        ts = int(utc_now.timestamp())
        with open(dir_data+'timer.ini','w+') as timer:
            timer.write(str(ts))

        for sub in subs:    
            log('Working on: '+sub)
            getposts(sub)
            refreshposts(sub)
        with open(dir_data+'timer.ini','r') as timer:
            ts = int(timer.read())
        utc_now = datetime.datetime.utcnow()
        ns = int(utc_now.timestamp())

        wait = timeout-(ns-ts)
        if wait < 0: wait = 0
        log('waiting: '+str(wait))
        time.sleep(wait)
    return None





if __name__ == '__main__':
    #r_client.captureMessage('Reddit scraper initiated.')
    cycle()
