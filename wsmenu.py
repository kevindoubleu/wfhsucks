import wsutils
import wsprinter

def menu(choices, funcs, beforechoices=None, afterchoices=None,):
    """
    choices: list
    funcs: list of funcs
    beforechoices: list of funcs
    afterchoices: list of funcs
    """

    choice = 0
    while True:
        if beforechoices is not None:
            for f in beforechoices:
                f()
        i = 0
        for choice in choices:
            if choice[:2] == "//":
                print choice[2:]
            elif choice[0] == " ":
                lastspace = choice.rfind('  ')+2
                print choice[:lastspace] + str(i+1) + ". {}".format(choice[lastspace:])
                i += 1
            else:
                print str(i+1) + ". {}".format(choices[i])
                i += 1
        print "0. Back"
        if afterchoices is not None:
            for f in afterchoices:
                f()
        
        try:
            choice = int(wsutils.simpleinput(">> "))
        except:
            break

        if choice == 0:
            break
        else:
            try:
                funcs[choice-1]()
            except:
                pass
    return choice
