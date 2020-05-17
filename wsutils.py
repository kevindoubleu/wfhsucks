import time
import datetime
import sys

def getchar():
    print "Enter to continue"
    try:
        input()
        print ""
    except:
        print ""
        return

def simpleinput(prompt):
    try:
        sys.stdin.flush()
    except:
        pass

    try:
        return raw_input(prompt)
    except KeyboardInterrupt:
        exit()
    except:
        return

def getidx(prompt, items):
    try:
        idx = int(simpleinput(prompt))-1
    except:
        return
    try:
        return items[idx]
    except:
        return

def gettimestamp(prompt, format):
    try:
        stamp = time.mktime(datetime.datetime.strptime(simpleinput(prompt), format).timetuple())
        return stamp
    except:
        return