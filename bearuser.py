import insultdict
import time
import sys
import re
import random

RESPONSES_TABLE="data/responses.txt"

def one_of(l):
    l = list(l)
    return l[random.randint(0,len(l)-1)]

class ResponseDict():
    def __init__(self):
        self.responsesByPrefixByMood={}
    def load(self,filename):
        for line in open(filename,'r'):
            try:
                match = re.search(r"([\d-]*)\s+([\d-]*)\s+(.*)",line)
                if match is None: continue
                position = int(match.group(1))
                mood = int(match.group(2))
                text = match.group(3).strip()
                response_list = self.responsesByPrefixByMood.setdefault(position,{}).setdefault(mood,[])
                response_list.append(text)
            except(ValueError,IndexError):
                pass
            
    def formatString(self,s,details):
        print details
        inserts = {
            'user_name': details["bear_user"].user.name
        }
        def do_replace(match):
            return inserts.get(match.group(1),match.group(0))
        return re.sub(r"{([^}]*)}",do_replace,s)
            
    def getResponse(self,mood,details):
        response_list1 = self.responsesByPrefixByMood[1][int(round(mood))]
        response_list2 = self.responsesByPrefixByMood[2][int(round(mood))]
        return " ".join([self.formatString(one_of(l),details) for l in [response_list1,response_list2]])
            
    
RESPONSES = ResponseDict()
RESPONSES.load(RESPONSES_TABLE)

class BearUser(object):
    def __init__(self, user):
        self.user = user
        self.mood = 0
        self.last_updated = time.time()
    def __repr__(self):
        return "user %s has made bear have mood %d - last talked at %s" %(self.user, self.mood, self.last_updated)

    def changeMood(self, mood_change):
        self.mood += mood_change
        if self.mood>2: self.mood = 2
        if self.mood<-2: self.mood = -2
        self.last_updated = time.time()

    def createReply(self, sentence, details):
        self.last_updated = time.time()
        rating = insultdict.INSULT_DICT.rateSentence(sentence)
        self.changeMood(rating/8.0)
        return RESPONSES.getResponse(self.mood, details)

def test():
    class User():
        def __init__(self):
            self.name="asdf"
    b = BearUser(User())
    print RESPONSES.getResponse(0,{'bear_user':b})
