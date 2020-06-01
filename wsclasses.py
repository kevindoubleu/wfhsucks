import wsutils

class ForumThread(object):
    "blueprint for 1 forum entry"

    def __init__(self, coursecode, coursecaption, courseid, classcaption, classid, threadcaption, threadid, threadreplies, threaddate, threadcontent):
        self.coursecode = coursecode
        self.coursecaption = coursecaption
        self.courseid = courseid
        self.classcaption = classcaption
        self.classid = classid
        self.threadcaption = threadcaption
        self.threadid = threadid
        self.threadreplies = threadreplies
        self.threaddate = threaddate
        self.threadcontent = threadcontent
        self.done = False

    def finish(self, hold=True):
        self.done = not self.done
        print "[!] %s is now %s" % (self.threadcaption, 'Finished' if self.done else 'Unfinished')
        if hold:
            wsutils.getchar()
    
    def getlink(self):
        print "\n----- Link -----"
        print self.coursecaption+" - "+self.classcaption+" - "+self.threadcaption
        print "https://binusmaya.binus.ac.id/newStudent/#/forum/reader."+self.threadid+"?id=1"
        print "----- Link -----\n"
        wsutils.getchar()

    def getcontent(self):
        print "\n----- Content -----"
        print self.coursecaption+" - "+self.classcaption+" - "+self.threadcaption
        print self.threadcontent
        print "----- Content -----\n"
        wsutils.getchar()
    
    def updatereplies(self, newreplies):
        self.threadreplies = newreplies

class Vidconf(object):
    "blueprint for 1 vidconf meeting"

    def __init__(self, coursecaption, week, session, date, time, meetnbr, pw, link):
        self.coursecaption = coursecaption
        self.week = week
        self.session = session
        self.date = date
        self.time = time
        self.meetnbr = meetnbr
        self.pw = pw
        self.link = link

    def getlink(self):
        print "\n----- Link -----"
        print self.coursecaption+" - Week "+self.week+" ("+self.date+" at "+self.time+")"
        print self.link
        print "----- Link -----\n"
        wsutils.getchar()
