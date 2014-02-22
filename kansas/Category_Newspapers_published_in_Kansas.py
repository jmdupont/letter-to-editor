"""
parsing of wikipedia
Category:Newspapers_published_in_Kansas
"""
from cache import cache
from html.parser import HTMLParser
import yaml


class MyHTMLParser(HTMLParser):
    """
    wikipedia html category parser
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.state = []
        self.href = ""
        self.obj = {}
        self.index = {}
        self.done = False

    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        if attrs:
            type_name = attrs[0][0]
            if type_name == "href":
                href = attrs[0][1]
                if href[0] == "h":
                    self.href = href
                else:
                    self.href = "https://en.wikipedia.org%s" % href
            if self.href == 'https://en.wikipedia.org':
                self.href = ""
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

    def handle_data(self, data):

        if self.state == [
            'html', 'body', 'div', 'div', 'div',
            'div',
            'div', 'div', 'table', 'tr', 'td', 'ul', 'li', 'a'
        ]:
            print(("Article", data, self.href))
            self.obj["name"] = data
            self.obj["page"] = self.href
            if "name" in self.obj:
                self.index[self.obj["name"]] = self.obj
            self.obj = {}

        else:
            # print(self.state,data)
            pass

        if self.done:
            return
        #self.obj[data] = str(self.href)
        self.href = ""

def main():
    """
    entry point
    """
    url = ('https://en.wikipedia.org/wiki/'
           'Category:Newspapers_published_in_Kansas')
    obj = cache(url)
    parser = MyHTMLParser()
    parser.feed(str(obj))

    for idx in parser.index:
        obj = parser.index[idx]
        for field in ("page", 'siteurl'):
            if field in obj:
                cache(obj[field])

    output = open('Category_Newspapers_published_in_Kansas.yaml', 'w')
    output.write(yaml.dump(parser.index, indent=4, default_flow_style=False))

if __name__ == "__main__":
    main()
