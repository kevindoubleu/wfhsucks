import wsutils
import wfhsucks
import json

class ForumThread(object):
    "blueprint for 1 forum entry"

    def __init__(self, coursecode, coursecaption, courseid, classcaption, classid, threadcaption, threadid, threadreplies, threaddate, threadcontent, threadanswer):
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
        self.threadanswer = threadanswer

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
    
    def getanswer(self):
        print "\n----- Answer -----"
        print self.answer
        print "----- Answer -----\n"
    
    def updatereplies(self, newreplies):
        self.threadreplies = newreplies
    
    def reply(self, headers, cookies):
        # get teacher's post id
        path = wfhsucks.forumpath+"getReply"
        payload = '{"threadid":"%s"}' % self.threadid
        replies = wfhsucks.send(path, payload, (headers, cookies))['rows']
        replies = json.loads(replies)
        replyid = replies[0]['PostID']
        # start the actual reply
        title = wsutils.simpleinput(wfhsucks.strings['prompts'][7])
        desc = wsutils.simpleinput(wfhsucks.strings['prompts'][8])
        payload = '{"title":"%s","description":"%s","action":"add","threadid":"%s?id=1","replyto":"%s","file":null}' % (title, desc, self.threadid, replyid)
        print "Summary"
        print "Title: "+title
        print "Desc / Content: "+desc
        confirm = wsutils.simpleinput("Confirm? (y/n): ")
        if confirm[0].lower() != 'y':
            print "[!] Reply cancelled"
            wsutils.getchar()
            return
        path = wfhsucks.forumpath+"saveReply"
        reply = wfhsucks.send(path, payload, (headers,cookies))
        print "Status: "+reply['message']

        if self.done == False:
            self.finish(hold=False)
        if len(self.threadanswer) == 0:
            self.threadanswer = desc

        wsutils.getchar()

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
