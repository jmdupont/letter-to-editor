"""
core fetching routine
"""
import os
import urllib.request
from urllib.error import HTTPError
from urllib.error import URLError
import yaml
import cgi

BADURLS = (
    'http://www.youtube.com/user/cjonline11',
    'http://www.twitter.com/udk_news',
    'https://www.facebook.com/ElDoradoTimes',
    'http://www.kstatecollegian.com/',
    'http://www.holtonrecorder.com/'
)
# http://www.sterling.edu/stir-newspaper


class Cache:
    """
    cache class
    """
    def __init__(
        self,
        inurl,
        outurl,
        header,
        charset,
        rawdata,
        data):
        self.inurl = inurl,
        self.outurl = outurl,
        self.header = header,
        self.charset = charset,
        self.rawdata = rawdata
        self.data = data

    def __str__(self):
        if self.data:
            return self.data
        else:
            return self.rawdata

def fetch(url):
    """
    fetch the url
    """
    tries = 5
    res = None
    while not res:
        if tries == 0:
            return None

        try:
            print(("going to open %s" % url))
            res = urllib.request.urlopen(url)
            return res

        except HTTPError as exp:
            print(("URL http Failed %s" % url))
            print(("URL http exp %s" % exp))
            if exp.code == 403:
                return None
            if exp.code == 404:
                return None
            return None

        except URLError as exp:
            print(("URL timeout %s" % url))
            print(("URL exp %s" % exp))
            reason = str(exp.reason)
            print(("URL exp reason '%s'" % reason))

            if reason == '[Errno -2] Name or service not known':
                # no route to host
                print(("bail out %s" % url))
                return None

            if reason == '[Errno 110] Connection timed out':
                print(("bail out %s" % url))
                return None

            res = None

        tries = tries - 1


def fetch2(filename, url):
    """
    run fetch and save the url
    """
    output_file = open(filename, "w")
    ###########
    res = fetch(url)
    if not res:
        return None
    print(("URL loaded: %s" % url))
    content_type = res.getheader("Content-Type")
    _, params = cgi.parse_header(content_type)
    if 'charset' in params:
        print(("CharSet %s" % params['charset']))
        charset = params['charset']
    else:
        print(("INFO %s" % res.info()))
        print(("param %s" % params))
        charset = "iso-8859-1"
    data = res.read()
    #string = data.decode()
    try:
        obj = {
            'inurl': url,
            'outurl': res.href,
            'header': res.info(),
            'charset': charset,
            'data': data.decode(charset),
        }
    except UnicodeDecodeError as exp:
        print("Unicode error :%s" % exp)
        obj = Cache(inurl=url,
                    outurl=res.href,
                    header=res.info(),
                    charset=charset,
                    rawdata=data)
    yaml.dump(obj, output_file)
    output_file.close()

def cache(url):
    name = url
    print(("load url: %s" % url))
    href = None
    name = name.replace("/", "").replace(".", "").replace(":", "")

    if url in BADURLS:
        print(("URL skipped %s" % url))
        data = "SKIPPED"
        return

    filename = "cache/%s.html" % name
    if not os.path.isdir("cache"):
        os.mkdir("cache")

    if os.path.isfile(filename):
        b = os.path.getsize(filename)
        if b < 100:
            os.remove(filename)

    if not os.path.isfile(filename):
        fetch2(filename, url)

    p = open(filename, "r")
    try:
        string = p.read()
    except:
        return "ERROR"

    try:
        return Cache(**yaml.load(string))
    except Exception as exp:
        print("is yaml?: %s" % string[0:10])
        print("yaml error: %s" % exp)
        return Cache(inurl=url,
                     outurl=url,
                     data=string,
                     header=None,
                     charset=None,
                     rawdata=None)
