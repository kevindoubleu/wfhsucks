class Table(object):
    """
    headers: list
    content: 2d list
        e.g. content[col][row]
        note: all elements must be str type
    alignments: str or list
    items: list of objects
        note: forums, vidvonfs, to be referenced
    """

    def __init__(self, headers, content, alignments, items=None):
        self.headers = headers
        self.content = content
        self.alignments = alignments
        self.rows = []
        self.items = items
        
        # validation
        if len(self.headers) != len(self.content) or len(self.headers) != len(self.alignments):
            raise Exception("Table headers, content, and alignments must contain same number of elements (columns)")
        for i in range(len(self.content)):
            if i > 0 and len(self.content[i]) != len(self.content[i-1]):
                raise Exception("All columns must have the same number of rows")

        # get max length of all cols
        self.lenarr = []
        for col in range(len(self.headers)):
            self.content[col].append(self.headers[col])
            self.lenarr.append(len(max([str(i) for i in self.content[col]], key=len)))
            self.content[col].pop()
        
        # table header
        self.rows += tblline(self.lenarr)
        self.rows += tblcontent(self.headers, self.lenarr, ['c' for i in self.headers])
        self.rows += tblline(self.lenarr)
        # table body
        for i in range(len(self.content[0])):
            line = []
            for j in range(len(self.lenarr)):
                line.append(self.content[j][i])
            self.rows += tblcontent(line, self.lenarr, self.alignments)
        self.rows += tblline(self.lenarr)

    def view(self):
        """
        prints some \\n then prints entire table
        """

        print '\n'*5
        print ''.join(self.rows)
    
    def clen(self, *colnums):
        """
        get column len based on column number
        colnums: ints
        """
        if len(colnums) == 1:
            return self.lenarr[colnums[0]]
        sum = -3
        for i in colnums:
            sum += self.lenarr[i] + 3
        return sum

    def addrow(self, idx, row):
        self.rows.insert(idx, row)
        return self
    def delrow(self, idx):
        self.rows.pop(idx)
        return self

    def numrows(self):
        return len(self.rows)
    def numcols(self):
        return len(self.headers)

def tblline(widths):
    """
    widths: list
    """

    line = "+"
    for w in widths:
        line += "-"*(w+2) + "+"
    return line+"\n"

def tblcontent(contents, widths, alignments):
    """
    contents: list
    widths: list
    alignments: str or list
    """

    if len(contents) != len(widths):
        raise Exception("Table content and widths contain different number of columns")

    line = "|"
    for i in range(len(contents)):
        if alignments[i] == 'c':
            line += " {:^{}} |".format(contents[i],widths[i])
        elif alignments[i] == 'l':
            line += " {:<{}} |".format(contents[i],widths[i])
        elif alignments[i] == 'r':
            line += " {:>{}} |".format(contents[i],widths[i])
    return line+"\n"
