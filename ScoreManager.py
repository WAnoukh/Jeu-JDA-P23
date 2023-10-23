import datetime

from PIL import Image
import json
import os
from datetime import date

class Score:
    score = None
    userName = None

    def __init__(self, score, userName):
        self.score = score
        self.userName = userName


class ScoreBoard:
    scores = []
    path = ""

    def __init__(self, path):
        self.path = path
        self.ReadScore()

    def AddScore(self, score, store=True):
        if len(self.scores) == 0:
            self.scores.append(score)
        else:
            inserted = False
            for i in range(len(self.scores)):
                if self.scores[i].score < score.score:
                    self.scores.insert(i, score)
                    inserted = True
                    break
            if not inserted:
                self.scores.append(score)
        if store:
            self.StoreScore()

    def StoreScore(self):
        convertedScore = [{"Score": sc.score, "UserName": sc.userName} for sc in self.scores]
        f = open(self.path, "w")
        with f as outfile:
            json.dump(convertedScore, outfile)
        f.close()
        sauvpath = self.path+"_sauv_"+str(date.today())+"-H"+str(datetime.datetime.today().hour)
        if not os.path.isfile(sauvpath):
            f = open(sauvpath, "w")
            with f as outfile:
                json.dump(convertedScore, outfile)
            f.close()

    def NextScore(self, score):
        i = -1
        for saveScore in self.scores:
            if saveScore.score < score:
                break
            i += 1
        if i == -1:
            return None, i+2
        return self.scores[i].score, i+2

    def ReadScore(self):
        try:
            f = open(self.path, "r")
        except:
            self.StoreScore()
            f = open(self.path, "r")
        try :
            ls = json.load(f)
            f.close()
        except:
            f.close()
            f = open(self.path, "a+")
            f.write('[{"Score": 999999999999, "UserName": "FileCorruptedCallAdmin"}]')
            f.close()
            f = open(self.path, "r")
            ls = json.load(f)
            f.close()

        for dic in ls:
            newScore = Score(dic["Score"], dic["UserName"])
            self.AddScore(newScore, store=False)

    def Top5(self):
        return self.scores[:5]
