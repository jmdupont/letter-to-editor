from cache import cache
from html.parser import HTMLParser
import yaml

# create a subclass and override the handler methods
names = {}


class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.state = []
        self.href = ""
        self.field = []
        self.obj = {}
        self.objs = []
        self.index = {}
        self.done = False

    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        if attrs:
            if self.state[0:8] == ['html', 'head', 'meta', 'body', 'div',
                                   'div', 'div', 'div']:
            #                print ("Encountered a start tag:", tag)
            #print ("D:  %s:" % (self.state))
                type_name = attrs[0][0]
                if type_name == "href":
                    href = attrs[0][1]
                    if href == 'clearfloat':
                        self.done = True
                        return

                    if href[0] == "h":
                        self.href = href
                    else:
                        url = "http://www.usnpl.com/%s" % href
                        self.href = url

            if self.href == 'http://www.usnpl.com/address/npmail.php':
                self.href = ""
        self.href = self.href.strip().rstrip()
        self.href = self.href.replace(" ", "%20")
        if self.href.find(" ") > 0:
            print(self.href)

        self.state.append(tag)

    def handle_endtag(self, tag):
        if self.done:
            return

        #print ("Encountered an end tag :", tag)
        self.state.pop()
        #self.field = []

    def handle_data(self, data):

        if self.done:
            return

        if self.state[0:8] == ['html', 'head', 'meta', 'body', 'div',
                               'div', 'div', 'div']:
            data = data.replace("\n", "")
            data = data.strip().rstrip()
            if (data):
                if data == "(":
                    pass
                elif data == ')(':
                    pass
                else:

                    #print ("D2: %s" % (data))
                    if data == "for address downloads.":
                        self.field = []

                    if data in (
                            '?',
                            '-',
                            '- Facebook',
                            '- Google+',
                            '- Twitter',
                            '.',
                            'Announcements',
                            'Info',
                            'More',
                            'State Google News',
                            'TV Stations',
                            'US Newspapers',
                            'USNPL',
                            'USNPL has address downloads for',
                            'and',
                            'Statewide',
                            'College Newspapers',
                            'Magazines',
                            '&',
                            '(A) for Address, phone, fax, editor, translate',
                            '(C) for County Results',
                            '(F) for Facebook',
                            '(T) for Twitter',
                            '(V) for Video',
                            '(W) for Local Weather',
                            'Click',
                            'Forecast',
                            'Newspapers',
                            'Untitled Document',
                            'here',
                            'for address downloads.',
                            'Craigslist for State',
                            'State Newspapers',
                            'State TV Stations',
                            'State Radio Stations',
                            'State Colleges',
                            'State Website',
                            'State Parks',
                            'Museums',
                            'Libraries',
                            'State Census',
                            'US Census by County',
                            'County Listing by City',
                            'State Governor',
                            'State House',
                            'State Senate',
                            'State Constitution',
                            'US House',
                            'US Senate',
                            'City Listing by County',
                    ):
                        return

                    elif data == ")":
                        #print ("Field:" + str(self.field))
                        #self.obj[data] = str(self.href)
                        self.href = ""
                        self.objs.append(self.obj)
                        obj = self.obj
                        self.obj = {}

                        address = []
                        name = ""
                        city = ""
                        for k in obj.keys():
                            if k not in ("A", "F", "T", "V", "C", "W"):
                                v = obj[k]
                                if not v:
                                    city = k
                                else:
                                    name = k

                                if len(k) > 2:
                                    address.append(k)
                                else:
                                    print ("WARN %s" % k)
                        # http://www.usnpl.com/addr/aaddressresult.php?id=1167

                        if (name):
                            obj['name'] = name
                            if (obj[name]):
                                obj['named'] = obj[name]
                            obj.pop(name)
                        else:
                            return

                        if city:
                            if (obj[city]):
                                obj['city_'] = obj[city]

                            obj['city'] = city
                            obj.pop(city)
                        else:
                            return

                        self.index["%s,%s" % (city, name)] = obj
                    else:
                        #print ("'%s'" % data)
                        self.obj[data] = str(self.href)
                        self.href = ""

string = cache("http://www.usnpl.com/ksnews.php")
parser = MyHTMLParser()
parser.feed(string)


for idx in parser.index:
    obj = parser.index[idx]

    # "W", eather, leave that out
    for a in ("A", "F", "T", "V", "C", "named", "city_"):
        if a in obj:
            cache(obj[a])

o = open('usnpl.yaml', 'w')
o.write(yaml.dump(parser.index, indent=4, default_flow_style=False))
