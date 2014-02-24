"""
parsing of wikipedia
Category:Newspapers_published_in_Kansas
"""
from cache import cache
from html.parser import HTMLParser
import yaml
import mwparserfromhell

class WikipediaPage:
    def __init__(self, page):
        self.page =page
        _str = str(page)
        #print (_str) 
        wikicode = mwparserfromhell.parse(_str)
        templates = wikicode.filter_templates()
        for x in templates:
            print ("template name %s" % x.name)
#            print ("para %s" % x.params)
            for p in x.params :
                print ("name: %s" % p.name)
                print ("value: %s" % p.value)

            #print ("item %s" % x)


class WikipediaParser(HTMLParser):
    """
    wikipedia html parser
    """
    def __init__(self):
        super().__init__()
        self.state = [] # tag stack
        self.a_state = [] # attr stack
        self.done = False
        self.obj = {}
        self.href = "" # the last href found
        self.index = {} # resulting index from page
        self.look_for_end = None

    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        self.href = ""
        if attrs:
            type_name = attrs[0][0]
            if type_name == "href":
                href = attrs[0][1]
                if href[0] == "h":
                    self.href = href
                else:
                    href=href.strip("\\\"")
                    href=href.rstrip("\\\"")
                    self.href = "https://en.wikipedia.org%s" % href
                self.href = self.href.strip().rstrip()
                self.href = self.href.replace(" ", "%20")
                self.on_href(self.href)
                # if self.href:
                #     if self.href.find('wikipedia.org') == -1 :
                #         print("Check HREF:%s" % (self.href))

        self.state.append(tag)
        d={}
        for x  in attrs:
            #print(x)
            d[x[0]]=x[1]

#        print("ATTR:%s"%d)
        d['__tag__']=tag
        d['__data__']=[]
        self.a_state.append(d)

    def handle_data(self, data):
        if len(self.a_state) == 0 :
            self.a_state.append({
                    "__data__" : []
                    }
                )
        self.a_state[-1]['__data__'].append(data)

    def handle_endtag(self, tag):
        if self.done:
            return
        if (self.look_for_end):
            if self.look_for_end.at_end(tag):
                self.look_for_end = None
        self.state.pop()
        self.a_state.pop()

    def on_href(self, href):
        pass

class WikipediaCatParser(WikipediaParser):
    """
    wikipedia html category parser
    """
    def __init__(self):
        super().__init__()

    def handle_data(self, data):
        super().handle_data(data)

        if self.state == [
            'html', 'body', 'div', 'div', 'div',
            'div',
            'div', 'div', 'table', 'tr', 'td', 'ul', 'li', 'a'
        ]:
            #print(("Article", data, self.href))
            self.obj["name"] = data
            self.obj["page"] = self.href
            if "name" in self.obj:
                self.index[self.obj["name"]] = self.obj
                #print ("adding data: %s" % self.obj)
            self.obj = {}
        else:
            # print(self.state,data)
            pass

        if self.done:
            return
        #self.obj[data] = str(self.href)
        self.href = ""

class WikipediaPageParser(WikipediaParser):
    """
    wikipedia html page parser
    """
    def __init__(self):
        super().__init__()
        self.ws = self.OfficialWebsite(self)
        self.infobox = self.InfoBox(self)

    class InfoBox :
        def __init__(self, parent):
            self.parent = parent

        def start(self, data):
            """
            handle the data that started this
            """
            #print ("ib start: %s %s :" % (self.parent.state,data))

        def data(self, data):
            """
            """
            #data = data.strip().rstrip()
            #print ("ib data %s :" % (self.parent.a_state[-1]))

        def at_end(self, tag):
            """
            is it at the end?            
            """
            a = self.parent.a_state[-1]

            if self.parent.state == ['html', 'body', 'div', 'div', 'div', 'table'] :
                print ("ib at end %s :" % ( a ))
                print (self.parent.state)
                return True
            else:
                if 'scope' in a:
                    if a['scope']== 'row':
                        if '__tag__' in a :
                            if a['__tag__'] == 'th':
                                pass
                                #print ("Title %s" % a['__data__'])

                                # ib inside {'__data__': ['\n', '\n', '\n'], '__tag__': 'tr'} :
                                # ib inside {'scope:' 'row', '__data__': ['Owner(s)'], '__tag__': 'th', 'style': 'text-align:left;'} :
                                # ib inside {'__data__': ['Rudy and Kathy Taylor'], '__tag__': 'td'} :
                                # ib inside {'__data__': ['\n', '\n', '\n'], '__tag__': 'tr'} :
                                
                #print (self.parent.state)
                #print ("ib inside %s :" % (self.parent.a_state[-1]))

                

            #print ("WS:Check end %s, %s" % (self.parent.state, tag))
            #if self.parent.state == ['html', 'body', 'div', 'div', 'div', 'table'] :
            #    return True

        
    class OfficialWebsite :
        def __init__(self, parent):
            self.parent = parent

        def start(self, data):
            """
            handle the data that started this
            """
            #print ("ws start: %s %s :" % (self.parent.state,data))

        def data(self, data):
            data = data.strip().rstrip()
            if self.parent.state[-1] == "a":
                if self.parent.href:
                    print ("data %s :" % (data))
                if data:
                    #print ("data %s :" % (data))
                    self.parent.obj['official_website']=data

        def at_end(self, tag):
            """
            is it at the end?
            """
            #print ("WS:Check end %s, %s" % (self.parent.state, tag))
            if self.parent.state == ['html', 'body', 'div', 'div', 'div', 'table'] :
                return True


    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)

        a = self.a_state[-1]
        if (
            'class' in a and
            a['class'] == 'infobox vcard' and 
            '__tag__' in a and
            a['__tag__'] == 'table'
            ):
            #
            self.look_for_end = self.infobox
            


    def handle_data(self, data):
        super().handle_data(data)

        if self.look_for_end:
            self.look_for_end.data(data)
            return

        if self.state == ['html', 'head', 'title'] :
            self.handle_title(data)
            return

        if self.state == ['html', 'body', 'div', 'div', 'div', 'table', 'tr', 'th'] :
            if data.lower() ==  'official website':
                # collect the next
                #['html', 'body', 'div', 'div', 'div', 'table', 'tr', 'td', 'a'] http://www.wyecho.com/
                # stop with
                self.look_for_end = self.ws
                self.ws.start(data)
                return

        if self.state == ['html', 'body', 'div', 'div', 'div', 'table', 'caption']:
            """
            """
            #ws start:  Anthony Republican, The :
            print ("Caption %s"  % self.a_state)

            
            # Caption 
            # [
            #     {'__data__': ['\n']
            #      }, 
            #     {
            #         'class': 'client-nojs',
            #         '__data__': ['\n', '\n'], 
            #         '__tag__': 'html', 
            #         'lang': 'en', 
            #         'dir': 'ltr'
            #         },
            #     {
            #         'class': 'mediawiki ltr sitedir-ltr ns-0 ns-subject page-Anderson_County_Review skin-vector action-view vector-animateLayout',
            #         '__tag__': 'body', 
            #         '__data__': ['\n\t\t', '\n\t\t', '\n\t\t']}, 
            #     {
            #         'class': 'mw-body', 
            #         'id': 'content', 
            #      '__data__': 
            #         ['\n\t\t\t', '\n\t\t\t', '\n\t\t\t\t\t\t', '\n\t\t\t\t\t\t', '\n\t\t\t'], 
            #         '__tag__': 'div', 'role': 'main'},
            #     {
            #         'id': 'bodyContent', 
            #         '__data__': ['\n\t\t\t\t\t\t\t\t', '\n\t\t\t\t\t\t\t\t', '\n\t\t\t\t\t\t\t\t\t\t\t\t', '\n\t\t\t\t'], 
            #         '__tag__': 'div'}, 
            #     {'class': 'mw-content-ltr', 'id': 'mw-content-text', 'lang': 'en', 
            #      '__data__': [], '__tag__': 'div', 'dir': 'ltr'}, 

            #     {'class': 'infobox vcard', 'cellspacing': '3', '__tag__': 'table', 
            #      '__data__': ['\n'], 'style': 'border-spacing:3px;width:22em;'}, 

            #     {
            #'class': 'fn org',
            #'__tag__': 'caption', 
            #      '__data__': ['Anderson County Review'], 'style': 'font-style: italic;'}]
            
        else:
            #print ("data start: %s" % (self.state))
            
            """
            """


        d = data.strip().rstrip()
        if (d):
            """
            """
            #print ("ws start: %s %s %s:" % (self.state[-5:],d, self.href))
            #print(str(self.a_state))
            #print(self.a_state[-1]. ('class', 'infobox vcard')

        if self.done:
            return

    def handle_title(self, title):
        #print ("title %s" % title)
        self.obj['title']=title.replace(" - Wikipedia, the free encyclopedia",'')

    def on_href(self, href):
        if href.find('en.wikipedia.org') >= 0:
            if href.find("&action=edit&section=1") > 0: 
                x = href.replace('&action=edit&section=1','&action=raw')
                print ("Get %s" % href)
                obj2 = cache(x)
                w= WikipediaPage(obj2)

            pass
        elif href.startswith('https://donate.wikimedia.org'):
            pass
        elif href.startswith('http://en.wikipedia.org'):
            pass
        else:
            print ("href %s" % href)


def main():
    """
    entry point
    """
    url = ('https://en.wikipedia.org/wiki/'
           'Category:Newspapers_published_in_Kansas')
    obj = cache(url)
    parser = WikipediaCatParser()
    strd = str(obj)
    parser.feed(strd)

    for idx in parser.index:
        obj = parser.index[idx]
        for field in ("page", 'siteurl'):
            if field in obj:
                val = obj[field]
                if val:
                    obj2 = cache(val)
                    p=WikipediaPageParser()
                    p.feed(str(obj2))
                    p.obj['url']=val
                    #print("FOUND:%s" % str(p.obj))


    output = open('Category_Newspapers_published_in_Kansas.yaml', 'w')
    output.write(yaml.dump(parser.index, indent=4, default_flow_style=False))

if __name__ == "__main__":
    main()
