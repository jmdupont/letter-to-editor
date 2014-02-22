import yaml
import csv
from cache import cache

index = {}
with open('media_in_kansas.csv', 'r') as csvfile:
    data = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in data:
        #print ("ROW :" + ', '.join(row))
        if row[0] == "Name":
            continue
        obj = {
            'name': row[0],
            'website': row[1],
            'ksa_site': row[2],
            'wikipedia': row[3],
            'phone': row[4],
            'fax': row[5],
            'address': row[6],
            'editor': row[7],
            'twitter': row[8],
            'facebook': row[9],
            'contact_page': row[10],
            'user_forum': row[11],
        }
        # if not obj['ksa_site' ] :
            #print ("ROW :" + str(obj))
        if obj['name'] not in index:
            index[obj['name']] = obj
        else:
            raise Exception(obj['name'])


for item in list(index.keys()):

    obj = index[item]
#    print (obj)
    for field in ("website", "wikipedia", "twitter", "facebook",
                  "contact_page", "user_forum"):
        if field in obj:
            v = obj[field]
            if v:
                print(("TODO %s" % v))
                if v[0:3] == "www":
                    v = "http://" + v
                elif v[0] == "?":
                    continue
                elif v.startswith('http://'):
                    cache(v)
                elif v.startswith('https://'):
                    cache(v)
                else:
                    cache("http://" + v)

o = open('media_in_kansas.yaml', 'w')
o.write(yaml.dump(index, indent=4, default_flow_style=False))
