#!/bin/python

import requests
import json
import urllib # parse forum title
import pickle # save n load
import datetime # convert date time format for easy reading
import time # batch finish/unfinish
import sys # args
import re # parse html into plaintext
import traceback # exception stack traces

import wsclasses
import wsutils
import wsprinter
import wsmenu

url = "http://binusmaya.binus.ac.id"
forumpath = "/services/ci/index.php/forum/"

acadyear = "2010"
headers = {
    "Referer": "https://binusmaya.binus.ac.id/newStudent/",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json;charset=utf-8"
}
cookies = {
    "PHPSESSID": "",
}

forum = []
vidconfs = []
myname = ""

strings = {
    "menus": [
        "Get link",
        "Finish/unfinish a thread",
        "Preview a thread",
        "Reply to a thread (NEW!)",
    ],
    "prompts": [
        "Select thread to get link from: ",
        "Select thread to finish/unfinish: ",
        "Select thread to preview: ",
        "Select course number to show threads from: ",
        "Select vidconf to get link from: ",
        "Input date1 (format is DD/MM/YYYY, example 30/12/2020): ",
        "Input date2 (format is DD/MM/YYYY, example 30/12/2020): ",
        "Input reply title: ",
        "Input reply description / content: ",
        "Select thread to reply to: ",
    ]
}


def savep(obj, filename):
    f = open(filename, "w")
    pickle.dump(obj, f)
    f.close()
def loadp(filename):
    f = open(filename, "r")
    return pickle.load(f)
def getmyname():
    path = "/services/ci/index.php/general/getBinusianData"
    mydata = send(path, "")
    myname = mydata['FIRST_NAME'] + " " + mydata['LAST_NAME']

    return myname

def send(path, payload, headersncookies=None):
    if headersncookies is not None:
        r = requests.post(url+path, headers=headersncookies[0], cookies=headersncookies[1], data=payload, verify=True)
    else:
        r = requests.post(url+path, headers=headers, cookies=cookies, data=payload, verify=True)
    
    if r.status_code != 200:
        print "[!] Error HTTP "+str(r.status_code)
        print r.text
        print path
        print payload
        if r.status_code == 500:
            print "[*] It's an HTTP 500 error, bimay's acting up, pls try again later"
        exit()

    try:
        jdata = r.json()
        return jdata
    except:
        return r.text

def getforum():
    global forum

    count = 0
    courses = getcourses()
    for course in courses:
        classes = getclasses(course)
        for kelas in classes:
            print "[*] Checking "+course['Caption']+" - "+kelas['Caption']
            threads = getthreads(course, kelas)

            for thread in threads:
                if thread['ID'] not in [t.threadid for t in forum]:
                    postdate, content, answer = getthreaddetails(thread)
                    t = wsclasses.ForumThread(
                        course['Caption'].encode("utf-8")[:8],
                        course['Caption'].encode("utf-8")[11:],
                        str(course['ID']).encode("utf-8"),
                        kelas['Caption'].encode("utf-8"),
                        str(kelas['ID']).encode("utf-8"),
                        urllib.unquote(thread['ForumThreadTitle'].encode("utf-8", 'ignore')),
                        str(thread['ID']).encode("utf-8"),
                        str(thread['replies']).encode("utf-8"),
                        postdate.encode("utf-8"),
                        content.encode("utf-8"),
                        answer.encode("utf-8")
                    )
                    print "[+] New thread: "+t.threadcaption
                    if len(t.threadanswer) > 0:
                        print "[*] My answer: " + t.threadanswer
                        t.finish(hold=False)
                    count += 1
                    forum.append(t)
                else: 
                    next((t for t in forum if t.threadid == thread['ID'])).updatereplies(str(thread['replies']).encode("utf-8"))
    print "[!] Done, %d new threads have been added" % count
    wsutils.getchar()
    print "[*] If problems occur, delete 'forum%s.data' file first and check if phpsessid already expired" % acadyear
    wsutils.getchar()
def getcourses():
    path = forumpath+"getCourse"
    payload = '{"acadCareer":"RS1","period":"%s","Institution":"BNS01"}' % acadyear
    result = send(path, payload)
    if result['status'] == "success":
        courses = result['rows']
        courses = json.loads(courses)
        return courses
    else:
        return []
def getclasses(course):
    path = forumpath+"getClass"
    payload = '{"acadCareer":"RS1","period":"%s","course":"%s","Institution":"BNS01"}' % (acadyear, course['ID'])
    classes = send(path, payload)['rows']
    classes = json.loads(classes)

    return classes
def getthreads(course, kelas):
    path = forumpath+"getThread"
    payload = '{"forumtypeid":1,"acadCareer":"RS1","period":"%s","course":"%s","classid":"%s","topic":"","Institution":"BNS01","SESSIONIDNUM":""}' % (acadyear, course['ID'], kelas['ID'])
    result = send(path, payload)
    if result['status'] == "success":
        threads = result['rows']
        threads = json.loads(threads)
        return threads
    else:
        return []
def getthreaddetails(thread):
    path = forumpath+"getReply"
    payload = '{"threadid":"%s"}' % thread['ID']
    replies = send(path, payload)['rows']
    replies = json.loads(replies)

    postdate = replies[0]['PostDate']

    content = replies[0]['Name']+"\n\n"+replies[0]['PostContent']
    content = "\n".join(content.splitlines())
    content = re.sub('<[^<]+?>', '', content)

    answer = ""
    for r in replies:
        if r['Name'] == myname:
            answer = r['PostContent']
            break

    return postdate, content, answer
def getthreaddate(thread):
    path = forumpath+"getReply"
    payload = '{"threadid":"%s"}' % thread['ID']
    replies = send(path, payload)['rows']
    replies = json.loads(replies)
    postdate = replies[0]['PostDate']

    return postdate
def getthreadcontent(thread):
    path = forumpath+"getReply"
    payload = '{"threadid":"%s"}' % thread['ID']
    replies = send(path, payload)['rows']
    replies = json.loads(replies)
    content = replies[0]['Name']+"\n\n"+replies[0]['PostContent']
    content = "\n".join(content.splitlines())
    content = re.sub('<[^<]+?>', '', content)

    return content
def getthreadanswer(thread):
    path = forumpath+"getReply"
    payload = '{"threadid":"%s"}' % thread['ID']
    replies = send(path, payload)['rows']
    replies = json.loads(replies)
    for r in replies:
        if r['Name'] == myname:
            return r['PostContent']
    return ""

def getvidconfs():
    global vidconfs

    classes = []
    coursethreadsamples = []
    for t in forum:
        if t.courseid+t.classid not in classes:
            classes.append(t.courseid+t.classid)
            coursethreadsamples.append(t)

    count = 0
    for c in coursethreadsamples:
        print "[*] Checking "+c.coursecaption+" - "+c.classcaption
        path = "/services/ci/index.php/student/classes/nextClass/%s/%s" % (acadyear, c.courseid)
        try:
            classdata = send(path, "")
        except:
            print "[!] Problem occurred, make sure you're logged in to bimay and the phpsessid is valid"
            return

        for cd in classdata:
            classnbr = cd['CLASS_NBR']
            vclist = getcoursevclist(c, classnbr)

            if not vclist:
                continue
            
            for vc in vclist:
                if vc.meetnbr not in [v.meetnbr for v in vidconfs]:
                    print "[+] New upcoming vidconf: "+vc.coursecaption+" - Week "+vc.week+" ("+vc.date+" at "+vc.time+")"
                    count += 1
                    vidconfs.append(vc)

    # immediately sort vc by date
    vidconfs.sort(key=lambda x: (getattr(x, 'date'), getattr(x, 'time')))

    print "[!] Done, %d new vidconfs have been added" % count
    wsutils.getchar()
    print "[*] If problems occur, delete 'vidconf%s.data' file first and check if phpsessid already expired" % acadyear
    wsutils.getchar()
def getcoursevclist(course, classnbr):
    path = "/services/ci/index.php/BlendedLearning/VideoConference/getList/%s/%s/%s/%s" % (course.coursecode, course.courseid, acadyear, classnbr)
    htmltbl = send(path, "")

    if "No Data Available" in htmltbl:
        return

    start = 0
    vidconfdata = []
    while htmltbl.find("</td>", start) != -1:
        end = htmltbl.find("</td>", start)
        vidconfdata.append(htmltbl[htmltbl.find("<td>", start)+4:end])
        start = end+1
    
    vclist = []
    while len(vidconfdata):
        vc = wsclasses.Vidconf(
            course.coursecaption,
            vidconfdata[1], 
            vidconfdata[2], 
            datetime.datetime.strptime(vidconfdata[3], "%b %d, %Y").strftime("%Y-%m-%d"),
            vidconfdata[4], 
            vidconfdata[5], 
            vidconfdata[6], 
            vidconfdata[7][vidconfdata[7].find("https://binus.zoom.us/"):vidconfdata[7].find("\"></span>")]
        )
        vclist.append(vc)
        vidconfdata = vidconfdata[8:]

    return vclist

def sortforum(key, rev, arr=None):
    # if arr == None:
    global forum
    if type(getattr(forum[0], key)) is 'str':
        forum.sort(key=lambda x: getattr(x, key).upper(), reverse=rev)
    else:
        forum.sort(key=lambda x: getattr(x, key), reverse=rev)
def sortmenu():
    keys = ['coursecaption', 'classcaption', 'threadcaption', 'threaddate', 'done', 'threadreplies']

    wsmenu.menu(
        [
            'Course asc', 'Class asc', 'Thread asc', 'Create date asc', 'Finished/unfinished asc', 'Replies asc',
            'Course dsc', 'Class dsc', 'Thread dsc', 'Create date dsc', 'Finished/unfinished dsc', 'Replies dsc' 
        ],
        beforechoices=[
            lambda: initalltbl().view()
        ],
        funcs=[
            lambda: sortforum('coursecaption', False),
            lambda: sortforum('classcaption', False),
            lambda: sortforum('threadcaption', False),
            lambda: sortforum('threaddate', False),
            lambda: sortforum('done', False),
            lambda: sortforum('threadreplies', False),
            lambda: sortforum('coursecaption', True),
            lambda: sortforum('classcaption', True),
            lambda: sortforum('threadcaption', True),
            lambda: sortforum('threaddate', True),
            lambda: sortforum('done', True),
            lambda: sortforum('threadreplies', True),
        ]
    )

def unfinishedmenu():
    unfinisheds = []
    for t in forum:
        if not t.done:
            unfinisheds.append(t)
    wsmenu.menu(
        [
            strings['menus'][0],
            strings['menus'][1],
            strings['menus'][2],
            strings['menus'][3]
        ],
        beforechoices=[
            lambda: wsprinter.Table(
                ['No', 'Course', 'Class', 'Thread', 'Finished', 'Created at', 'Replies'],
                [
                    [i+1 for i in range(len(unfinisheds))],
                    [t.coursecaption for t in unfinisheds],
                    [t.classcaption for t in unfinisheds],
                    [t.threadcaption for t in unfinisheds],
                    ['Yes' if t.done else 'No' for t in unfinisheds],
                    [datetime.datetime.strptime(t.threaddate[:10], "%Y-%m-%d").strftime("%d-%b-%Y") for t in unfinisheds],
                    [t.threadreplies for t in unfinisheds]
                ],
                "rrrlrrr"
            ).view()
        ],
        funcs=[
            lambda: wsclasses.ForumThread.getlink(
                wsutils.getidx(strings['prompts'][0],unfinisheds)),
            lambda: wsclasses.ForumThread.finish(
                wsutils.getidx(strings['prompts'][1],unfinisheds)),
            lambda: wsclasses.ForumThread.getcontent(
                wsutils.getidx(strings['prompts'][2],unfinisheds)),
            lambda: wsclasses.ForumThread.reply(
                wsutils.getidx(strings['prompts'][9],unfinisheds),headers,cookies),
        ]
    )

def coursemenu():
    # remove total row
    ovtbl = initoverviewtbl()
    ovtbl = ovtbl.delrow(ovtbl.numrows()-1).delrow(ovtbl.numrows()-1)
    # ask which course to view
    ovtbl.view()
    try:
        chosencourseidx = wsutils.getidx(strings['prompts'][3],[i for i in range(len(initcoursetbls()))])
        chosencoursetbl = initcoursetbls()[chosencourseidx]
    except:
        return
    threads = chosencoursetbl.items

    wsmenu.menu(
        [
            strings['menus'][0],
            strings['menus'][1],
            strings['menus'][2],
            strings['menus'][3],
        ],
        beforechoices=[
            lambda: initcoursetbls()[chosencourseidx].view()
        ],
        funcs=[
            lambda: wsclasses.ForumThread.getlink(
                wsutils.getidx(strings['prompts'][0],threads)),
            lambda: wsclasses.ForumThread.finish(
                wsutils.getidx(strings['prompts'][1],threads)),
            lambda: wsclasses.ForumThread.getcontent(
                wsutils.getidx(strings['prompts'][2],threads)),
            lambda: wsclasses.ForumThread.reply(
                wsutils.getidx(strings['prompts'][9],threads),headers,cookies),
        ]
    )
def allmenu():
    wsmenu.menu(
        [
            strings['menus'][0],
            strings['menus'][1],
            strings['menus'][2],
            strings['menus'][3],
        ],
        beforechoices=[
            lambda: initalltbl().view()
        ],
        funcs=[
            lambda: wsclasses.ForumThread.getlink(
                wsutils.getidx(strings['prompts'][0],forum)),
            lambda: wsclasses.ForumThread.finish(
                wsutils.getidx(strings['prompts'][1],forum)),
            lambda: wsclasses.ForumThread.getcontent(
                wsutils.getidx(strings['prompts'][2],forum)),
                lambda: wsclasses.ForumThread.reply(
                wsutils.getidx(strings['prompts'][9],forum),headers,cookies),
        ]
    )

def batchtoggle(timestamp1, timestamp2, status):
    for t in forum:
        tstamp = time.mktime(datetime.datetime.strptime(t.threaddate[:10], "%Y-%m-%d").timetuple())
        if timestamp1 <= tstamp and tstamp <= timestamp2 and t.done != status:
            t.finish(False)
    wsutils.getchar()
def batchmenu():
    wsmenu.menu(
        [
            "Finish all threads from date1 until date2",
            "Unfinish all threads from date1 until date2"
        ],
        beforechoices=[
            lambda: initalltbl().view()
        ],
        funcs=[
            lambda: batchtoggle(wsutils.gettimestamp(strings['prompts'][5], "%d/%m/%Y"), wsutils.gettimestamp(strings['prompts'][6], "%d/%m/%Y"), True),
            lambda: batchtoggle(wsutils.gettimestamp(strings['prompts'][5], "%d/%m/%Y"), wsutils.gettimestamp(strings['prompts'][6], "%d/%m/%Y"), False)
        ]
    )

def vcmenu():
    wsmenu.menu(
        [
            strings['menus'][0],
            # "delete finished vidconfs"
        ],
        beforechoices=[
            lambda: initvctbl().view()
        ],
        funcs=[
            lambda: wsclasses.Vidconf.getlink(wsutils.getidx(strings['prompts'][4],vidconfs))
        ]
    )

def getcoursenames():
    coursenames = []
    for t in forum:
        if t.coursecaption not in coursenames:
            coursenames.append(t.coursecaption)

    return coursenames
def initalltbl():
    return wsprinter.Table(
        ['No', 'Course', 'Class', 'Thread', 'Finished', 'Created at', 'Replies'],
        [
            [i+1 for i in range(len(forum))],
            [t.coursecaption for t in forum],
            [t.classcaption for t in forum],
            [t.threadcaption for t in forum],
            ['Yes' if t.done else 'No' for t in forum],
            [datetime.datetime.strptime(t.threaddate[:10], "%Y-%m-%d").strftime("%d-%b-%Y") for t in forum],
            [t.threadreplies for t in forum]
        ],
        "rrrlrrr",
        forum
    )
def initoverviewtbl():
    coursenames = getcoursenames()

    unfinishedcount = [0 for i in range(len(coursenames))]
    for t in forum:
        if not t.done:
            unfinishedcount[coursenames.index(t.coursecaption)] += 1
    newests = []
    for c in coursenames:
        newests.append(max([t.threaddate for t in forum if t.coursecaption == c])[:10])
    tbl = wsprinter.Table(
        ['No', 'Your Courses', 'Unfinished', 'Newest Post'],
        [
            [i+1 for i in range(len(coursenames))],
            coursenames,
            unfinishedcount,
            [datetime.datetime.strptime(newest, "%Y-%m-%d").strftime("%d-%b-%Y") for newest in newests]
        ],
        "rlrr"
    )

    # add total row
    if len(forum) != 0:
        tbl.addrow(len(tbl.rows),
            wsprinter.tblcontent(
            [
                'Total',
                sum(unfinishedcount),
                datetime.datetime.strptime(max(newests), "%Y-%m-%d").strftime("%d-%b-%Y")
            ],
            [tbl.clen(0,1),tbl.clen(2),tbl.clen(3)],
            "rrr"
        ))
        tbl.addrow(len(tbl.rows), wsprinter.tblline([tbl.clen(0,1),tbl.clen(2),tbl.clen(3)]))

    return tbl
def initcoursetbls():
    coursenames = getcoursenames()
    coursetbls = []
    for c in coursenames:
        threads = []
        unfinished = 0
        for t in forum:
            if t.coursecaption == c:
                threads.append(t)
                if not t.done:
                    unfinished += 1
        
        tbl = wsprinter.Table(
                ['No', 'Class', 'Thread', 'Finished', 'Created at', 'Replies'],
                [
                    [i+1 for i in range(len(threads))],
                    [t.classcaption for t in threads],
                    [t.threadcaption for t in threads],
                    ['Yes' if t.done else 'No' for t in threads],
                    [datetime.datetime.strptime(t.threaddate[:10], "%Y-%m-%d").strftime("%d-%b-%Y") for t in threads],
                    [t.threadreplies for t in threads]
                ],
                "rrlrrr",
                threads
        )
        # add header row
        tbl.addrow(0,
            wsprinter.tblline([sum(i+2 for i in tbl.lenarr)+3])
        )
        tbl.addrow(1,
            wsprinter.tblcontent(
                [c],
                [sum(i+2 for i in tbl.lenarr)+3],
                "c"
            )
        )
        # add total row
        tbl.addrow(tbl.numrows(),
            wsprinter.tblcontent(
                ['Total', unfinished, ''],
                [
                    tbl.clen(0,1,2),
                    tbl.clen(3),
                    tbl.clen(4,5)
                ],
                "rrr"
            )
        )
        tbl.addrow(tbl.numrows(),
            wsprinter.tblline(
                [
                    tbl.clen(0,1,2),
                    tbl.clen(3),
                    tbl.clen(4,5)
                ]
            )
        )

        coursetbls.append(tbl)
    return coursetbls
def initvctbl():
    return wsprinter.Table(
        ['No', 'Course', 'Week', 'Session', 'Date', 'Time', 'Meeting No', 'Password'],
        [
            [i+1 for i in range(len(vidconfs))],
            [v.coursecaption for v in vidconfs],
            [v.week for v in vidconfs],
            [v.session for v in vidconfs],
            [datetime.datetime.strptime(v.date, "%Y-%m-%d").strftime("%d-%b-%Y") for v in vidconfs],
            [v.time for v in vidconfs],
            [v.meetnbr for v in vidconfs],
            [v.pw for v in vidconfs]
        ],
        "rlrrrrrr"
    )
def initmainmenutbl():
    return initoverviewtbl()

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
    wsutils.getchar()
def help():
    print "wfhsucks if a \"program\" i made to help me deal with stuff like"
    print "    checking all forum for new threads easily"
    print "    making sure i finish all my forum assignments"
    print "    not having to deal with bimay's loading speed"
    print "    get all vidconf schedules easily"
    print "using it alone feels like a waste tho, so here ya go, hope it helps"
    print "stay safe"
    print "more info about the program at https://kevindoubleu.github.io/projects/python/wfhsucks/index.html"
    print "any improvements are welcome at https://github.com/kevindoubleu/wfhsucks"
    wsutils.getchar()
def faq(hold=None):
    print "FAQ"
    print "Q: why do you need my phpsessid ?"
    print "A: to get and acces into bimay, bimay needs your phpsessid to make sure ur a legit student"
    print ""
    print "Q: are you stealing my phpsessid ?"
    print "A: no, you can check all the requests made by this script with wireshark or something, or check the source code yourself"
    print ""
    print "Q: I can't use my phpsessid ?"
    print "A: bimay probably gave you a new phpsessid, refresh / relog and get the new phpsessid"
    print ""
    print "Q: loading new forum data doesn't do anything ?"
    print "A: bimay probably gave you a new phpsessid, refresh / relog and get the new phpsessid"
    if hold != False:
        wsutils.getchar()

def parseargs():
    if len(sys.argv) < 2:
        print "Usage: python %s phpsessid [academic_year]" % __file__
        print "    phpsessid : php session id from bimay, it's in your browser cookies"
        print "    academic_year : your current academic year"
        print "                    e.g. 1920, default is 2010 for b22 on 5th semester"
        faq(False)
        exit()

    global acadyear, cookies
    if len(sys.argv) == 3:
        acadyear = str(sys.argv[2])
    cookies['PHPSESSID'] = str(sys.argv[1])
def main():
    parseargs()
    global myname
    myname = getmyname()
    try:
        global forum
        forum = loadp("forum%s.data" % acadyear)
    except:
        print "[+] Initiating forum data, first time run only"
        try:
            print "[+] Hello there "+myname
            getforum()
        except Exception:
            traceback.print_exc()
            print "[!] Problem occurred, make sure you're logged in to bimay and the phpsessid is valid"
            exit()
    try:
        global vidconfs
        vidconfs = loadp("vidconf%s.data" % acadyear)
    except:
        print "[+] Initiating vidconf data (needs forum data), first time run only"
        try:
            getvidconfs()
        except:
            print "[!] Problem occurred, make sure you're logged in to bimay and the phpsessid is valid"
            exit()
    
    wsmenu.menu(
        [
            "//Welcome " + myname,
            "//wfhsucks main menu",
            "//    Forum",
            "        Check for new threads",
            "        Print all unfinished threads (NEW!)",
            "        Print threads from a course (NEW!)",
            "        Print threads from all courses (NEW!)",
            "        Batch finish/unfinish",
            "        Sort table",
            "//    Video conference (obsolete and no longer maintained, use https://myclass.apps.binus.ac.id instead)",
            "        Check for new upcoming video conferences",
            "        Print all upcoming video conferences",
            "//    Others",
            "        Quick fix table printing issues",
            "        Quick info",
            "        FAQ"
        ],
        beforechoices=[
            lambda: initmainmenutbl().view()    
        ],
        afterchoices=[
            lambda: savep(forum, "forum%s.data" % acadyear),
            lambda: savep(vidconfs, "vidconf%s.data" % acadyear)
        ],
        funcs=[
            lambda: getforum(),
            lambda: unfinishedmenu(),
            lambda: coursemenu(),
            lambda: allmenu(),
            lambda: batchmenu(),
            lambda: sortmenu(),
            lambda: getvidconfs(),
            lambda: vcmenu(),
            lambda: fixissues(),
            lambda: help(),
            lambda: faq()
        ]
    )

if __name__ == "__main__":
    main()
