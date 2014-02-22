import urllib.request
from html.parser import HTMLParser
import os
import yaml
from cache import cache
# create a subclass and override the handler methods
names = {}


class MyHTMLParser(HTMLParser):

    def __init__(self, url, name):
        HTMLParser.__init__(self)
        self.state = []
        self.field = []
        self.role = None

        self.attr = {
            'src_url': url,
            'src_name': name,
            'roles': {}
        }

    def handle_starttag(self, tag, attrs):
        #print ("Encountered a start tag:", tag)
        if tag in ("table", "td", "th", "tr"):
            self.state.append(tag)
        if tag == "tr":
            self.field = []

    def handle_endtag(self, tag):
        #print ("Encountered an end tag :", tag)
        if tag in ("table", "td", "th", "tr"):
            self.state.pop()

        if tag == "tr":
            if len(self.field) == 0:
                return

            if self.field[0] in (
                    'Ad Submission Email',
                    'Ad Deadline',
                    'Days of Week Published',
                    'Mon.',
                    'T',
                    'M',
                    'Display Column Specifications',
                    'Number of Display Columns',
                    'One Column',
                    'Two Columns',
                    'Three Columns',
                    'Four Columns',
                    'Five Columns',
                    'Six Columns',
                    'Seven Columns',
                    'Newspaper Information'):
                pass
            elif self.field[0] in (
                    'Editor',
                    'Publisher',
                    'Managing Editor',
                    'Advertising Director',
            ):
                self.role = self.field[0]
                self.attr['roles'][self.role] = {}
            elif self.field[0] in (
                    'Name',
                    'Email',
            ):
                key = self.field[0]

                if len(self.field) > 1:
                    val = self.field[1]

                    #print ("Field '%s'" % (self.field))
                    self.attr['roles'][self.role][key] = val
                else:
                    self.attr['roles'][self.role][key] = "NONE"

            elif self.field[0] in (
                    'Address',
                    'Alternate Address',
                    'City',
                    'State',
                    'ZIP',
                    'County',
                    'Phone',
                    'Fax',
                    'Website',
                    'Member Type',
                    'Type',
                    'Newspaper Name',
                    'Circulation'):
                key = self.field[0]

                if len(self.field) > 1:
                    val = self.field[1]
                    #print ("Key '%s' = '%s'" % (key, val))
                    self.attr[key] = val
                else:
                    self.attr[key] = "NONE"
                    # if self.field[0]  in (
                    #'Newspaper Name',):
                #print ("D:  %s" % (self.attr))
                #print ("D:  %s" % (self.roles))

                # self.attr={}
                # self.roles={}

            self.field = []

    def handle_data(self, data):
        if self.state and data:

            self.field.append(data)
            # if data not in names :
            # print ("D:  %s | %s:" % (self.state, data))
            #     print (data)
            #     names[data]=1

data = {}
f = open('kansas_simple.csv')
for l in f.readlines():
    l = l.strip().rstrip()
    parts = l.split("|")
    url = parts[0]
    name = parts[1]
    parts = url.split("=")
    number = parts[1]
    filename = "cache/cache_item_%s.html" % number
    if not os.path.isfile(filename):
        p = open(filename, "w")
        res = urllib.request.urlopen(url)
        data = res.read()
        string = data.decode()
        p.write(string)
        p.close()

    p = open(filename, "r")
    string = p.read()
    parser = MyHTMLParser(url, name)
    parser.feed(string)
    data[name] = parser.attr

for item in list(data.keys()):
    obj = data[item]
#    print (obj)
    if "Website" in obj:
        v = obj["Website"]
        # patch this
        v = v.replace("stir.sterling.edu",
                      "http://www.sterling.edu/stir-newspaper")
        cache(v)

#print (yaml.dump(data))
o = open('kansas_simple.yaml', 'w')
o.write(yaml.dump(data, indent=4, default_flow_style=False))
