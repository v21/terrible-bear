import insultdict
import time
import sys
import re
import random

RESPONSES_TABLE="data/responses.txt"

class ResponseDict():
    def __init__(self):
        self.responses={}
    def load(self,filename):
        for line in open(filename,'r'):
            try:
                match = re.search(r"\s+",line)
                if match is None: continue
                mood = int(line[:match.start()])
                text = line[match.end():].strip()
                response_list = self.responses.setdefault(mood,[])
                response_list.append(text)
            except(ValueError,IndexError):
                pass
            
    def getResponse(self,mood):
        response_list = self.responses[int(round(mood))]
        return response_list[random.randint(0,len(response_list)-1)]
    
            
    
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

    def createReply(self, sentence):
        self.last_updated = time.time()
        rating = insultdict.INSULT_DICT.rateSentence(sentence)
        self.changeMood(rating/8.0)
        return RESPONSES.getResponse(self.mood)
        print >> sys.stderr , self
