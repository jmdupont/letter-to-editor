
from cache import cache
#import urllib.request
from html.parser import HTMLParser
#import os
import yaml
#import pprint
import re
#from urllib.error import HTTPError
BASE = "http://www.mondotimes.com"


class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.state = []
        self.href = ""
        self.obj = {}
        self.index = {}
        self.done = False

    def handle_starttag(self, tag, attrs):

        # close unclosed tr
        if self.state == ['html', 'body', 'div', 'div', 'table', 'tr', 'tr', ]:
            self.state = ['html', 'body', 'div', 'div', 'table', 'tr', ]

        #      print("STATE %s" % self.state)

        if self.done:
            return
        if attrs:

        #            print("ATTRS %s" % attrs)
            type_name = attrs[0][0]
            if type_name == "href":
                href = attrs[0][1]
                if href[0] == "h":
                    self.href = href
                else:
                    url = "%s%s" % (BASE, href)
                    self.href = url

        self.href = self.href.strip().rstrip()
        self.href = self.href.replace(" ", "%20")
        if self.href.find(" ") > 0:
            print((self.href))
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

        if self.state == ['html', 'body', 'div', 'div', 'table',
                          'tr', 'td', 'a', 'a']:
            if data not in self.index:
                self.index[data] = {
                    'name': data,
                    'info_page': self.href
                }
                # print(self.state,data,self.href)


class MondoInfoHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.state = []
        self.href = ""
        self.obj = {}
        self.index = {
            "sources": []
        }
        self.done = False
        self.title = []

    def matches(self, regex, text, names):
        m = re.match(regex, text)
        count = 0
        if m:
            count = 1
            for name in names:
                g = m.group(count)
                self.index[name] = g
                count = count + 1
        return count > 0

    def handle_starttag(self, tag, attrs):
        if attrs:
            type_name = attrs[0][0]
            if type_name == "href":
                href = attrs[0][1]
                if href[0] == "h":
                    self.href = href
                else:
                    url = "%s%s" % (BASE, href)
                    self.href = url
        self.href = self.href.strip().rstrip()
        self.href = self.href.replace(" ", "%20")
        if self.href.find(" ") > 0:
            print((self.href))
        self.state.append(tag)

    def handle_endtag(self, tag):
        if self.done:
            return

        if self.state == ['html', 'head', 'title']:
            if self.matches(
                regex=r'(.+) \- (daily newspaper|newspaper)'
                ' in (.+) (?:with|covering) (.+)',
                text=" ".join(self.title),
                names=[
                    "title",
                    "type",
                    "location",
                    "coverage"
                ]
            ):
                self.sources(self.title)
            else:
                raise Exception(self.title)

        #print ("Encountered an end tag :", tag)
        self.state.pop()

    def sources(self, data):

        self.index["sources"].append(
            [
                ",".join(self.state),
                data,
                self.href
            ]
        )

    def handle_data(self, data):
        if self.done:
            return
        data = data.strip()
        data = data.rstrip()
        data = data.replace("\n", "")
        data = data.replace("\t", "")
        if data.find("function(") > 0:
            return
        if not data:
            return

        if self.href.startswith("http://www.facebook.com/MondoTimes"):
            return

        if self.href.startswith("http://www.mondocode.com/"):
            return

        if self.href.startswith("http://www.easymedialist.com/"):
            return

        if self.href.startswith("http://www.mondotimes.com/"):
            if self.href.startswith("http://www.mondotimes.com/include/click"):
                cache(self.href)
            else:
                return

        if data not in self.index:
            if self.state == ['html', 'head', 'title']:
                self.title.append(data)
                return

            elif self.matches(r'For more (.+) contact information,',
                              data, ["name"]):
                self.sources(data)

            elif data.startswith("Mailing address:"):
                data = data.replace("Mailing address: ", "")
                self.index['address'] = data

            elif self.matches(r'Search for (.+) newspaper obituaries',
                              data,
                              ["name"]):
                pass

            elif self.matches(r'(.+) is the '
                              '(news editor|news director'
                              '|managing editor|editor)'
                              ' of the (.+)', data,
                              ["editor", "editor_role", "name"]):
                self.sources(data)

            elif self.matches(
                r'(\w+.+) replaced (\w+.+) who (earlier|previously)'
                ' replaced (\w+.+) as the '
                '(news editor|managing editor|editor) of the (.+)', data,
                [
                    "temp_new_editor",
                    "temp_old_editor",
                    "temp_old2_editor",
                    "temp_role",
                    "test_name"
                ]
            ):
                self.sources(data)
                role = self.index['temp_role']
                role = role.replace(" ", "_")
                new_e = self.index['temp_new_editor']
                old_e = self.index['temp_old_editor']
                old_e2 = self.index['temp_old2_editor']

                assert(len(new_e) < 20)
                assert(len(role) < 20)
                assert(len(old_e) < 20)
                assert(len(old_e2) < 20)

                self.index['old_%s' % role] = old_e
                self.index['old2_%s' % role] = old_e2
                self.index['new_%s' % role] = new_e
                del self.index['temp_role']
                del self.index['temp_new_editor']
                del self.index['temp_old_editor']
                del self.index['temp_old2_editor']

            elif (
                self.matches(
                    r'In (.+) (\d+) (\w+.+) replaced (\w+.+) (as the|as) '
                    '(managing editor|editor) of the (.+)',
                    data,
                    [
                        "replace_date",
                        "temp_new_editor",
                        "temp_old_editor",
                        "temp_role",
                        "name"
                    ]
                )

                #  X replaced Y who earlier replaced Z as the R of the T

                    or
                    (
                        self.matches(
                            r'(\w+.+) replaced (\w+.+) as the '
                            '(news editor|managing editor|editor)'
                            ' of the (.+)', data,
                            [
                                "temp_new_editor",
                                "temp_old_editor",
                                "temp_role",
                                "test_name"
                            ]
                        ))):
                self.sources(data)
                role = self.index['temp_role']
                role = role.replace(" ", "_")
                new_e = self.index['temp_new_editor']
                old_e = self.index['temp_old_editor']

                if len(new_e) > 20:
                    raise Exception(new_e)

                assert(len(role) < 20)
                assert(len(old_e) < 20)

                self.index['old_%s' % role] = old_e
                self.index['new_%s' % role] = new_e

                del self.index['temp_role']
                del self.index['temp_new_editor']
                del self.index['temp_old_editor']

            elif self.matches(r'(.+) is the news '
                              'editor of the (.+)',
                              data, ["news_editor", "name"]):
                self.sources(data)

            elif self.matches(r'(.+) was the editor when it folded (.+)',
                              data, ["last_editor"]):
                self.sources(data)

            elif self.matches(r'For more (.+) contact information',
                              data, ["name"]):
                pass

            elif data.find('The newspaper accepts only '
                           'local press release submissions.'):
                self.index['accepts_submissions'] = "local"
                self.sources(data)

            elif self.matches(r'covering (.+),', data, ["coverage2"]):
                self.sources(data)

            elif self.matches(r'Search for (.+),', data, ["name"]):
                pass

            elif data.find('Contact Information') >= 0:
                pass

            else:
                if 'name' in self.index:
                    if data == self.index['name']:
                        return

                #raise Exception("cannot parse '%s'" % data)
                self.index[data] = self.href

url = '%s/newspapers/usa/kansas.html' % BASE
res = cache(url)
string = res['data']
parser = MyHTMLParser()
parser.feed(string)

for idx in parser.index:
    obj = parser.index[idx]

    # "W", eather, leave that out
    for a in ("city_url", "info_page", "publisher_page"):
        if a in obj:
            url = obj[a]
            page = cache(url)
            info_parser = MondoInfoHTMLParser()
            info_parser.feed(page['data'])
            parser.index[idx].update(dict(info_parser.index))

o = open('mondotimes.yaml', 'w')
o.write(
    yaml.dump(
        parser.index,
        indent=4,
        default_flow_style=False
    )
)
