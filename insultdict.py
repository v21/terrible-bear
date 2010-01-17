import re

def reverse(i):
    return list(i)[::-1]

EMOTION_TABLE="data/EmotionLookupTable.txt"
NEGATING_TABLE="data/NegatingWordList.txt"
        
NEGATING_WORDS=map(str.strip,open(NEGATING_TABLE,"r"))

class InsultDict():
    def __init__(self):
        self.insults = {}
        self.log = ""
    def _log(self, text):
        self.log+=text+"\n";
    def load(self,filename):
        file = open(filename, 'r')
        for line in file:
            try:
                items = line.split("\t")
                self.insults[items[0]] = float(items[1].strip())
            except(ValueError,IndexError):
                pass
                
    def rateWord(self,word):
        """Rate a single word"""
        if word in self.insults:
            return self.insults[word]
        for i in reverse(range(len(word))):
            subword = word[:i]+"*"
            if subword in self.insults:
                return self.insults[subword]
                
    def rateSentence(self, sentence):
        """Rate a sentence, by splitting into rateable words"""
        words = re.split(r"[^\w']*",sentence)
        rated_words = []
        ratings = []
        scale = 1
        for word in words:
            word = word.lower()
            if word in NEGATING_WORDS:
                scale *= -1
                continue
            rating = self.rateWord(word)
            if rating:
                rated_words.append(word)
                ratings.append(scale*rating)
                scale = 1
        basic_rating = sum(ratings)
        
        magic_insult = hash(tuple(sorted(rated_words))) % 255
        magic_rating = 0
        if magic_insult>230:
            magic_rating = 3
        if magic_insult<20:
            magic_rating = -3
            
        return basic_rating + magic_rating
        
INSULT_DICT = InsultDict()
INSULT_DICT.load(EMOTION_TABLE)

def test():
    SAMPLES="""
    You vile hideous animal.
    I hate you, you are a terrible bear.
    I don't hate you, I detest you.
    I don't like you
    You are useless
    You are an idiot
    You are not an idiot
    You are not not an idiot"""

    for sentence in SAMPLES.split("\n")[1:]:
        print sentence
        print INSULT_DICT.rateSentence(sentence);
