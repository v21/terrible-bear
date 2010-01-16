"""
twitterbot

  A twitter IRC bot. Twitterbot connected to an IRC server and idles in
  a channel, polling a twitter account and broadcasting all updates to
  friends.
  
USAGE

  twitterbot [config_file]

CONFIG_FILE

  The config file is an ini-style file that must contain the following:

[twitter]
email: <twitter_account_email>
password: <twitter_account_password>

and optionally:
[debug]
debug: False

  If no config file is given "twitterbot.ini" will be used by default.
"""

BOT_VERSION = "TwitterBot 1.0 (http://mike.verdone.ca/twitter)"

IRC_BOLD = chr(0x02)
IRC_ITALIC = chr(0x16)
IRC_UNDERLINE = chr(0x1f)
IRC_REGULAR = chr(0x0f)

import sys
import time
from dateutil.parser import parse
from ConfigParser import SafeConfigParser
from heapq import heappop, heappush
import traceback
import os.path
import twitter

from twitter import TwitterError
import re
from htmlentitydefs import name2codepoint




def htmlentitydecode(s):
    return re.sub(
        '&(%s);' % '|'.join(name2codepoint),
        lambda m: unichr(name2codepoint[m.group(1)]), s)

debug_flag = False

def debug(msg):
    # uncomment this for debug text stuff
    if debug_flag:
        print >> sys.stderr, msg
    else:
        pass 


class SchedTask(object):
    def __init__(self, task, delta, repeat):
        self.task = task
        self.delta = delta
        self.next = time.time()
        self.repeat = repeat

    def __repr__(self):
        return "<SchedTask %s next:%i delta:%i>" %(
            self.task.__name__, self.next, self.delta)
    
    def __cmp__(self, other):
        return cmp(self.next, other.next)
    
    def __call__(self):
        return self.task()

class Scheduler(object):
    def __init__(self, tasks):
        self.task_heap = []
        for task in tasks:
            heappush(self.task_heap, task)
    
    def next_task(self):
        debug("next_task")
        now = time.time()
        task = heappop(self.task_heap)
        wait = task.next - now
        task.next = now + task.delta
        if task.repeat:
            heappush(self.task_heap, task)
        if (wait > 0):
            time.sleep(wait)
        task()
        debug("tasks: " + str(self.task_heap))

    def add_task(self, task):
        heappush(self.task_heap, task)

    def run_forever(self):
        while True:
            self.next_task()


class TwitterBot(object):
    def __init__(self, configFilename):
        self.configFilename = configFilename
        self.config = load_config(self.configFilename)
        self.twitter = twitter.Api(
            username=self.config.get('twitter', 'email'),
            password=self.config.get('twitter', 'password'))

        self.sched = Scheduler(
           #(SchedTask(self.process_events, 1),
           (SchedTask(self.check_dms, 120, True),
           SchedTask(self.start_game_to_v21, 30, False),
            SchedTask(self.check_replies, 30, True)))
           #  SchedTask(self.stay_joined, 120)))
        self.lastDMsUpdate = time.gmtime()
        self.lastRepliesUpdate = time.gmtime()
        self.lastUpdate = time.gmtime()

    def start_game_to_v21(self):
        self.start_game("v21", "you should really generalize this bit")
    def start_game(self, follower, message):
        try:
            self.twitter.CreateFriendship(follower)
            self.twitter.PostDirectMessage(follower, message)
            #some kind of database action
        except Exception, e:
            print >> sys.stderr, "Exception while querying twitter:"
            traceback.print_exc(file=sys.stderr)
            return

    def check_dms(self):
        debug("In check_statuses")
        try:
            updates = self.twitter.GetDirectMessages()
        except Exception, e:
            print >> sys.stderr, "Exception while querying twitter:"
            traceback.print_exc(file=sys.stderr)
            return

        nextLastUpdate = self.lastDMsUpdate
        for update in updates:
            crt = parse(update.created_at).utctimetuple()
            if (crt > self.lastUpdate):
                text = (htmlentitydecode(
                    update.text.replace('\n', ' '))
                    .encode('utf-8', 'replace'))
                self.handle_dm(update)

                nextLastUpdate = crt
            else:
                break
        self.lastDMsUpdate = nextLastUpdate

    def check_replies(self):
        debug("In check_replies")
        try:
            updates = self.twitter.GetReplies()
        except Exception, e:
            print >> sys.stderr, "Exception while querying twitter:"
            traceback.print_exc(file=sys.stderr)
            return

        nextLastUpdate = self.lastRepliesUpdate
        for update in updates:
            crt = parse(update.created_at).utctimetuple()
            if (crt > self.lastUpdate):
                text = (htmlentitydecode(
                    update.text.replace('\n', ' '))
                    .encode('utf-8', 'replace'))
                self.handle_replies(update)

                nextLastUpdate = crt
            else:
                break
        self.lastRepliesUpdate = nextLastUpdate


    def handle_dm(self, update):
        message = "bear is feeling emotional"
        self.twitter.PostDirectMessage(update.sender_screen_name, message)

    def handle_replies(self, update):

        message = "bear says hello"
        self.twitter.PostUpdate(status="@%s %s"%(update.user.screen_name, message), in_reply_to_status_id=update.id)
    
    def run(self):
        while True:
            try:
                self.sched.run_forever()
            except KeyboardInterrupt:
                break
            except TwitterError, e:
                # twitter.com is probably down because it sucks. ignore the fault and keep going
                print >> sys.stderr, e
            #except Exception, e:
            #    print >> sys.stderr, e

def load_config(filename):
    defaults = dict(debug=dict(debug=False))
    cp = SafeConfigParser(defaults)
    cp.read((filename,))
    
    # attempt to read these properties-- they are required
    cp.get('twitter', 'email'),
    cp.get('twitter', 'password')
    try:
        global debug_flag
        debug_flag = cp.getboolean('debug', 'debug')
    except: #debug is optional
        pass

    return cp

def main():
    configFilename = "twitterbot.ini"
    if (sys.argv[1:]):
        configFilename = sys.argv[1]
        
    try:
        if not os.path.exists(configFilename):
            raise Exception()
        load_config(configFilename)
    except Exception, e:
        print >> sys.stderr, "Error while loading ini file %s" %(
            configFilename)
        print >> sys.stderr, e
        print >> sys.stderr, __doc__
        sys.exit(1)

    bot = TwitterBot(configFilename)
    return bot.run()

main()