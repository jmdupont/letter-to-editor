import os
import urllib.request
from urllib.error import HTTPError
from urllib.error import URLError
import yaml
import cgi

bad = (
    'http://www.youtube.com/user/cjonline11',
    'http://www.twitter.com/udk_news',
    'https://www.facebook.com/ElDoradoTimes',
    'http://www.kstatecollegian.com/',
    'http://www.holtonrecorder.com/'
)
# http://www.sterling.edu/stir-newspaper


def fetch(url):
    tries = 5
    res = None
    while(not res):
        if tries == 0:
            return None

        try:
            print ("going to open %s" % url)
            res = urllib.request.urlopen(url)
            #href = res.geturl()

        except HTTPError as exp:
            print("URL http Failed %s" % url)
            print("URL http exp %s" % exp)
            if exp.code == 403:
                return None
            if exp.code == 404:
                return None
            return None

        except URLError as exp:
            print("URL timeout %s" % url)
            print("URL exp %s" % exp)
            reason = str(exp.reason)
            print("URL exp reason '%s'" % reason)

            if reason == '[Errno -2] Name or service not known':
                # no route to host
                print("bail out %s" % url)
                return None

            if reason == '[Errno 110] Connection timed out':
                print("bail out %s" % url)
                return None

            res = None

        tries = tries - 1


def cache(url):
    name = url
    print("load url: %s" % url)
    href = None
    name = name.replace("/", "").replace(".", "").replace(":", "")

    if url in bad:
        print("URL skipped %s" % url)
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
        p = open(filename, "w")
        ###########
        res = fetch(url)
        if not res:
            return None
        print("URL loaded: %s" % url)

        #        for i in res.info():
        #            print ("I %s" %  i)
        ct = res.getheader("Content-Type")
        _, params = cgi.parse_header(ct)

        if 'charset' in params:
            print ("CharSet %s" % params['charset'])
            charset = params['charset']
        else:

            print ("INFO %s" % res.info())
            print ("param %s" % params)
            charset = "iso-8859-1"
        # : text/html; charset=utf-8
        # resp[0]['content-type']
        #print (res)
        #        print (dir(res))

        data = res.read()
        #string = data.decode()

        try:
            obj = {
                'inurl': url,
                'outurl': href,
                'header': res.info(),
                'charset': charset,
                'data': data.decode(charset),
            }
        except UnicodeDecodeError as e:
            print(e)
            obj = {
                'inurl': url,
                'outurl': href,
                'header': res.info(),
                'charset': charset,
                'rawdata': data,
            }

        yaml.dump(obj, p)

        p.close()
    p = open(filename, "r")
    try:
        string = p.read()
    except:
        return "ERROR"

    try:
        return yaml.load(string)
    except Exception as exp:
        print (exp)
        return {
            'inurl': url,
            'outurl': url,
            'data': string
        }
