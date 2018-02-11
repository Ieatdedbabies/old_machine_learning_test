from random import *

def DNA():
    mob = []
    totaltime = 20
    for a in xrange(2):
        for b in xrange(2):
            for c in xrange(-1,2):
                for d in xrange(-1,2):
                    temp = []
                    temp.append((a,b,c,d))
                    for n in xrange(randint(16, 16)):
                        mvtx = randint(-1,1)
                        mvty = randint(-1,1)
                        time = randint(5,totaltime)
                        temp.append((mvtx,mvty,time))
                    total = 0
                    for tottime in temp:
                        if len(tottime) != 4:
                            total += tottime[2]
                    if total > totaltime:
                        sub = (total - totaltime) / float(len(temp)-1)
                        for value in xrange(len(temp)):
                            if value:
                                temp[value] = (temp[value][0],
                                               temp[value][1],
                                               temp[value][2]-sub)
                    mob.append(temp)
    return mob
                
def newpop(amount):
    pop = []
    for i in xrange(amount):
        pop.append(DNA())
    return pop

##print newpop(1)[0][0]
