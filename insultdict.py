import re

def reverse(i):
    return list(i)[::-1]
        
NEGATING_WORDS=["not","don't","cannot","can't"]

class InsultDict():
    def __init__(self):
        self.insults = {}
        self.log = ""
    def _log(self, text):
        self.log+=text+"\n";
    def Load(self,filename):
        file = open(filename, 'r')
        for line in file:
            try:
                items = line.split("\t")
                self.insults[items[0]] = float(items[1].strip())
            except(ValueError,IndexError):
                pass
                
    def RateWord(self,word):
        """Rate a single word"""
        if word in self.insults:
            return self.insults[word]
        for i in reverse(range(len(word))):
            subword = word[:i]+"*"
            if subword in self.insults:
                return self.insults[subword]
                
    def RateSentence(self, sentence):
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
            rating = self.RateWord(word)
            if rating:
                rated_words.append(word)
                ratings.append(scale*rating)
        basic_rating = sum(ratings)
        
        magic_insult = hash(tuple(sorted(word))) % 255
        magic_rating = 0
        if magic_insult>230:
            magic_rating = 3
        if magic_insult<20:
            magic_rating = -3
            
        return basic_rating + magic_rating

dict_filename="EmotionLookupTable.txt"
insult_dict = InsultDict()
insult_dict.Load(dict_filename)

SAMPLES="""
You vile hideous animal.
I don't hate you, I detest you.
I don't like you"""

for sentence in SAMPLES.split("\n")[1:]:
    print sentence
    print insult_dict.RateSentence(sentence);