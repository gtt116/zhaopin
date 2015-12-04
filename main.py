import os
import time
import urllib2
import collections
import json
from datetime import datetime

from bs4 import BeautifulSoup as BS

PWD = os.path.dirname(__file__)
DATA_DIR = 'datas'
JSON_PATH = 'data.json'


def read_keywords():
    filepath = os.path.join(PWD, 'keywords.txt')
    kws = file(filepath, 'r').readlines()
    return [kw.strip() for kw in kws]


def save_result(keyword, count):
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d')

    directory = DATA_DIR
    path = os.path.join(PWD, directory, keyword)
    print "Save to file: %s" % path

    with file(path, 'a') as result:
        result.write("%s %s\n" % (now_str, count))


def generate_json():
    path = os.path.join(PWD, DATA_DIR)
    output = {}
    for result in os.listdir(path):

        date_count = collections.OrderedDict()

        file_path = os.path.join(PWD, DATA_DIR, result)
        data = open(file_path, 'r').readlines()

        for line in data:
            tokens = line.split()
            try:
                date_count[tokens[0]] = int(tokens[1])
            except TypeError:
                pass

        output[result] = date_count.items()

    with file(os.path.join(PWD, JSON_PATH), 'w') as outputfile:
        print "Dumping to %s" % outputfile
        outputfile.write(json.dumps(output))
        outputfile.flush()


def main():
    base_url = 'http://sou.zhaopin.com/jobs/searchresult.ashx?&kw=%(kw)s'

    for key in read_keywords():
        url = base_url % {'kw': key}
        print "Fetch page: %s" % url

        while True:
            try:
                response = urllib2.urlopen(url)
                body = response.read()
            except Exception as ex:
                print ex
                print 'retry after 1 second'
                time.sleep(1)
            else:
                break

        bs = BS(body, "html.parser")
        em = bs.find('span', class_="search_yx_tj").find('em')
        count = em.string
        print "Found count: %s" % count
        save_result(key, count)

    generate_json()
    print 'Done'

if __name__ == '__main__':
    main()
