#!/bin/python

import requests
import json
import urllib # parse forum title
import pickle # save n load
import datetime # convert date time format for easy reading
import time # batch finish/unfinish
import sys # args
import re # parse html into plaintext

url = "http://binusmaya.binus.ac.id"
frontpath = "/services/ci/index.php/forum/"

acadyear = "1920"
headers = {
    "Referer": "https://binusmaya.binus.ac.id/newStudent/",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json;charset=utf-8"
}
cookies = {
    "PHPSESSID": "",
}

forum = []
class Thread(object):
    "blueprint for 1 forum entry"

    def __init__(self, coursecaption, courseid, classcaption, classid, threadcaption, threadid, threadreplies, threaddate, threadcontent):
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
            getchar()

def savep(obj, filename):
    f = open(filename, "w")
    pickle.dump(obj, f)
    f.close()
def loadp(filename):
    f = open(filename, "r")
    return pickle.load(f)

def send(path, payload):
    r = requests.post(url+path, headers=headers, cookies=cookies, data=payload)
    if r.status_code != 200:
        print "Error HTTP "+str(r.status_code)
        exit()

    jdata = r.json()

    return jdata
def getforum():
    global forum

    existingthreads = []
    for t in forum:
        existingthreads.append(t.threadid)
    count = 0

    courses = getcourses()
    for course in courses:
        classes = getclasses(course)
        for kelas in classes:
            print "[*] Checking "+course['Caption']+" - "+kelas['Caption']
            threads = getthreads(course, kelas)

            for thread in threads:
                thread = Thread(
                    course['Caption'].encode("utf-8")[11:],
                    str(course['ID']).encode("utf-8"),
                    kelas['Caption'].encode("utf-8"),
                    str(kelas['ID']).encode("utf-8"),
                    urllib.unquote(thread['ForumThreadTitle'].encode("utf-8", 'ignore')),
                    str(thread['ID']).encode("utf-8"),
                    str(thread['replies']).encode("utf-8"),
                    getthreaddate(thread).encode("utf-8"),
                    getthreadcontent(thread).encode("utf-8")
                )

                if thread.threadid not in existingthreads:
                    print "[+] New thread: "+thread.threadcaption
                    count += 1
                    forum.append(thread)
    print "[!] Done, %d new threads have been added" % count
    getchar()
def getcourses():
    path = frontpath+"getCourse"
    payload = '{"acadCareer":"RS1","period":"%s","Institution":"BNS01"}' % acadyear
    courses = send(path, payload)['rows']
    courses = json.loads(courses)

    return courses
def getclasses(course):
    path = frontpath+"getClass"
    payload = '{"acadCareer":"RS1","period":"%s","course":"%s","Institution":"BNS01"}' % (acadyear, course['ID'])
    classes = send(path, payload)['rows']
    classes = json.loads(classes)

    return classes
def getthreads(course, kelas):
    path = frontpath+"getThread"
    payload = '{"forumtypeid":1,"acadCareer":"RS1","period":"%s","course":"%s","classid":"%s","topic":"","Institution":"BNS01","SESSIONIDNUM":""}' % (acadyear, course['ID'], kelas['ID'])
    threads = send(path, payload)['rows']
    threads = json.loads(threads)

    return threads
def getthreaddate(thread):
    path = frontpath+"getReply"
    payload = '{"threadid":"%s"}' % thread['ID']
    replies = send(path, payload)['rows']
    replies = json.loads(replies)
    postdate = replies[0]['PostDate']

    return postdate
def getthreadcontent(thread):
    path = frontpath+"getReply"
    payload = '{"threadid":"%s"}' % thread['ID']
    replies = send(path, payload)['rows']
    replies = json.loads(replies)
    content = replies[0]['Name']+"\n"+replies[0]['PostContent']
    content = "\n".join(content.splitlines())
    content = re.sub('<[^<]+?>', '', content)

    return content

def sort(key, rev):
    global forum
    if type(getattr(forum[0], key)) is 'str':
        forum.sort(key=lambda x: getattr(x, key).upper(), reverse=rev)
    else:
        forum.sort(key=lambda x: getattr(x, key), reverse=rev)
def sortmenu():
    choice = 0
    order = True
    keys = ['coursecaption', 'classcaption', 'threadcaption', 'threaddate', 'done', 'threadreplies']
    while True:
        pall()
        print "Sort table (%s) by:" % ('Descending' if order else 'Ascending')
        print "1. Course"
        print "2. Class"
        print "3. Thread"
        print "4. Create date"
        print "5. Finished/unfinished"
        print "6. Replies"
        print "9. Toggle ascending/descending"
        print "0. Back"

        choice = justinput(">> ")
        if choice == 0:
            break
        elif 1 <= choice and choice <= 6:
            sort(keys[choice-1], order)
        elif choice == 9:
            order = not order

def printgeneralmenu():
    print "1. Get link"
    print "2. Finish/unfinish a thread"
    print "3. Preview thread question/task"
def choosegeneralmenu(choice, thread):
    if choice == 1:
        idx = justinput("Select thread to get link from: ")
        try:
            getlink(thread[idx-1])
        except:
            return
    elif choice == 2:
        idx = justinput("Select thread to finish/unfinish: ")
        try:
            thread[idx-1].finish()
        except:
            return
    elif choice == 3:
        idx = justinput("Select thread to preview: ")
        try:
            getcontent(thread[idx-1])
        except:
            return

def pall(omit=True, unfinishedonly=False):
    if unfinishedonly:
        threads = []
        for t in forum:
            if not t.done:
                threads.append(t)
    else:
        threads = forum

    len1 = maxcolumnlen("coursecaption", threads)
    len2 = len("class")
    len3 = maxcolumnlen("threadcaption", threads)
    len4 = len("finished")
    len5 = len("created at")+1
    len6 = len("replies")
    lenarr = [3,len1,len2,len3,len4,len5,len6]

    tblline([i+2 for i in lenarr])
    tblcontent(
        ['No', 'Courses', 'Class', 'Thread', 'Finished', 'Created at', 'Replies'],
        lenarr, "ccccccc")
    tblline([i+2 for i in lenarr])

    prevcourse = ""
    prevclass = ""
    i = 1
    for t in threads:
        currcourse = t.coursecaption
        currclass = t.classcaption
        if omit:
            if prevcourse == currcourse:
                currcourse = ""
            else:
                prevcourse = currcourse
            if prevclass == currclass:
                currclass = ""
            else:
                prevclass = currclass
        tblcontent(
            [i,currcourse,currclass,t.threadcaption,'Yes' if t.done else 'No',datetime.datetime.strptime(t.threaddate[:10], "%Y-%m-%d").strftime("%d-%b-%Y"), t.threadreplies],
            lenarr, "rrrlrrr")
        i += 1
    tblline([i+2 for i in lenarr])
def allmenu():
    choice = 0
    tableomitted = True
    while True:
        pall(tableomitted)
        printgeneralmenu()
        print "4. Toggle table view (Current: %s)" % ('Omitted' if tableomitted else 'Full')
        print "0. Back"

        choice = justinput(">> ")
        if choice == 0:
            break
        elif 1 <= choice and choice <= 3:
            choosegeneralmenu(choice, forum)
        elif choice == 4:
            tableomitted = not tableomitted
def unfinishedmenu():
    threads = []
    for t in forum:
        if not t.done:
            threads.append(t)
    choice = 0
    while True:
        pall(False, True)
        printgeneralmenu()
        print "0. Back"
        
        choice = justinput(">> ")
        if choice == 0:
            break
        elif 1 <= choice and choice <= 3:
            choosegeneralmenu(choice, threads)

def pcourse(idx):
    coursenames = getcoursenames()
    if idx == -1:
        poverview(False)
        idx = input("Select course number to show threads from: ")
        try: # out of range ga
            coursenames[idx-1] 
        except:
            return

    threads = []
    for t in forum:
        if t.coursecaption == coursenames[idx-1]:
            threads.append(t)

    len1 = len("class")
    len2 = maxcolumnlen("threadcaption", threads)
    len3 = len("finished")
    len4 = len(" created at")
    len5 = len("Replies")
    lenarr = [3,len1,len2,len3,len4,len5]

    tblline([(len1+len2+len3+len4+len5+20)])
    tblcontent([coursenames[idx-1]],[(len1+len2+len3+len4+len5+18)],"c")
    tblline([i+2 for i in lenarr])
    tblcontent(
        ['No', 'Class', 'Thread', 'Finished', 'Created at', 'Replies'],
        lenarr, "cccccc")
    tblline([i+2 for i in lenarr])
    i = 1
    for t in threads:
        tblcontent(
            [i,t.classcaption,t.threadcaption, 'Yes' if t.done else 'No', datetime.datetime.strptime(t.threaddate[:10], "%Y-%m-%d").strftime("%d-%b-%Y"), t.threadreplies],
            lenarr, "rrrrrr")
        i += 1
    tblline([i+2 for i in lenarr])
    return idx
def coursemenu():
    coursenames = getcoursenames()
    coursethreads = []
    for c in range(len(coursenames)):
        threads = []
        for t in forum:
            if t.coursecaption == coursenames[c]:
                threads.append(t)
        coursethreads.append(threads)

    choice = 0
    courseidx = -1
    while True:
        courseidx = pcourse(courseidx)
        printgeneralmenu()
        print "0. Back"
        threads = coursethreads[courseidx-1]

        choice = justinput(">> ")
        if choice == 0:
            break
        elif 1 <= choice and choice <= 3:
            choosegeneralmenu(choice, threads)

def batchtoggle(timestamp1, timestamp2, status):
    for t in forum:
        tstamp = time.mktime(datetime.datetime.strptime(t.threaddate[:10], "%Y-%m-%d").timetuple())
        if timestamp1 <= tstamp and tstamp <= timestamp2 and t.done != status:
            t.finish(False)
def batchmenu():
    choice = 0
    while True:
        pall()
        print "1. Finish all threads from date1 until date2"
        print "2. Unfinish all threads from date1 until date2"
        print "0. Back"

        choice = justinput(">> ")
        if choice == 0:
            break
        elif choice == 1 or choice == 2:
            date1 = raw_input("Input date1 (format is DD/MM/YYYY, example 30/12/2020): ")
            date2 = raw_input("Input date2 (format is DD/MM/YYYY, example 30/12/2020): ")
            stamp1 = time.mktime(datetime.datetime.strptime(date1, "%d/%m/%Y").timetuple())
            stamp2 = time.mktime(datetime.datetime.strptime(date2, "%d/%m/%Y").timetuple())
            batchtoggle(stamp1, stamp2, (True if choice == 1 else False))
            getchar()

def poverview(showtotal=True):
    len1 = maxcolumnlen("coursecaption")
    len2 = len("unfinished")
    len3 = len("newest post")
    lenarr = [3,len1,len2,len3]

    tblline([i+2 for i in lenarr])
    tblcontent(['No', 'Your Courses', 'Unfinished', 'Newest Post'], lenarr, "cccc")
    tblline([i+2 for i in lenarr])
    
    coursenames = getcoursenames()
    total = 0
    totalnewest = 0
    i = 1
    for c in coursenames:
        count = 0
        newest = 0
        for t in forum:
            if t.coursecaption == c:
                tstamp = time.mktime(datetime.datetime.strptime(t.threaddate[:10], "%Y-%m-%d").timetuple())
                if tstamp > newest:
                    newest = tstamp
                if not t.done:
                    count += 1
        tblcontent(
            [i,c,count,datetime.datetime.fromtimestamp(newest).strftime("%d-%b-%Y")],
            lenarr, "rlrl")
        total += count
        if newest > totalnewest:
            totalnewest = newest
        i += 1
    tblline([i+2 for i in lenarr])
    if showtotal:
        tblcontent(
            ["Total", total, datetime.datetime.fromtimestamp(totalnewest).strftime("%d-%b-%Y")],
            [len1+6,len2,len3], "rrr")
        tblline([len1+2+6,len2+2,len3+2])

def getcoursenames():
    coursenames = []
    for t in forum:
        if t.coursecaption not in coursenames:
            coursenames.append(t.coursecaption)

    return coursenames
def getlink(thread):
    print thread.coursecaption+" - "+thread.classcaption+" - "+thread.threadcaption
    print "https://binusmaya.binus.ac.id/newStudent/#/forum/reader."+thread.threadid
    getchar()
def getcontent(thread):
    print thread.coursecaption+" - "+thread.classcaption+" - "+thread.threadcaption
    print thread.threadcontent
    getchar()

def maxcolumnlen(col, arr=None):
    data = []
    if not arr:
        for t in forum:
            data.append(getattr(t, col))
    else:
        for t in arr:
            data.append(getattr(t, col))
    return len(max(data, key=len))
def tblline(widths):
    line = "+"
    for w in widths:
        line += "-"*w + "+"
    print line
def tblcontent(contents, widths, alignment):
    if len(contents) != len(widths):
        print "[!] Table printing error"
        return
    line = "|"
    for i in range(len(contents)):
        if alignment[i] == 'c':
            line += " %s |" % (str(contents[i]).center(widths[i]))
        elif alignment[i] == 'l':
            line += " %-*s |" % (widths[i], str(contents[i]))
        elif alignment[i] == 'r':
            line += " %*s |" % (widths[i], str(contents[i]))
    print line

def getchar():
    print "Enter to continue"
    try:
        input()
    except:
        return
def justinput(prompt):
    while True:
        try:
            return input(prompt)
        except KeyboardInterrupt:
            exit()
        except:
            break
def fixissues():
    fixes = 0
    for t in forum:
        newcaptionchars = []
        fixed = False
        for i in t.threadcaption:
            if ord(i) < 128:
                newcaptionchars.append(i)
            else:
                newcaptionchars.append('-')
                fixed = True
        t.threadcaption = ''.join(newcaptionchars)
        if fixed:
            fixes += 1
        # t.threadcaption = ''.join([i if ord(i) < 128 else '-' for i in t.threadcaption])
    print "[!] Fixed %s issue(s)" % fixes
    getchar()
def parseargs():
    if len(sys.argv) < 2:
        print "Usage: python %s phpsessid [academic_year]" % __file__
        print "    phpsessid : php session id from bimay, it's in your browser cookies"
        print "    academic_year : your current academic year, e.g. 1920, default is 1920"
        exit()

    global acadyear, cookies
    if len(sys.argv) == 3:
        acadyear = str(sys.argv[2])
    cookies['PHPSESSID'] = str(sys.argv[1])
def main():
    parseargs()

    try:
        global forum
        forum = loadp("forumdata%s" % acadyear)
    except:
        print "[+] Initiating forum data, first time run only"
        try:
            getforum()
            print "[*] If problems occur, delete 'forumdata' file first and check if phpsessid already expired"
        except:
            print "[!] Problem occurred, make sure you're logged in to bimay and the phpsessid is valid"
            exit()
        getchar()
    
    choice = 0
    while True:
        poverview()
        print "wfhsucks main menu"
        print "1. Check for new threads"
        print "2. Print all unfinished threads"
        print "3. Print threads from a course"
        print "4. Print threads from all courses"
        print "5. Batch finish/unfinish"
        print "6. Sort table"
        print "8. Help"
        print "9. Quick fix table printing issues"
        print "0. Exit"
        savep(forum, "forumdata%s" % acadyear)

        choice = justinput(">> ")
        if choice == 0:
            break
        elif choice == 1:
            print "[*] Checking for new forums"
            getforum()
        elif choice == 2:
            unfinishedmenu()
        elif choice == 3:
            coursemenu()
        elif choice == 4:
            allmenu()
        elif choice == 5:
            batchmenu()
        elif choice == 6:
            sortmenu()
        elif choice == 8:
            print "wfhsucks if a \"program\" i made to help me deal with stuff like"
            print " checking all forum for new threads easily"
            print " making sure i finish all my forum assignments"
            print " not having to deal with bimay's loading speed"
            print "using it alone feels like a waste tho, so here ya go, hope it helps"
            print "stay safe"
            print "any improvements are welcome at https://github.com/kevindoubleu/wfhsucks"
            getchar()
        elif choice == 9:
            fixissues()

if __name__ == "__main__":
    main()
