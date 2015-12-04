#-*-coding:utf-8-*-
import os
import sys
PWD = os.path.dirname(__file__)
# After this, we can import module lagou from any workspace
sys.path.insert(0, PWD)

import traceback
import time
import urllib2
import collections
import json
from datetime import datetime

from bs4 import BeautifulSoup as BS

import lagou


DATA_DIR = 'datas'
JSON_PATH = 'data.json'


def read_keywords():
    filepath = os.path.join(PWD, 'keywords.txt')
    kws = file(filepath, 'r').readlines()
    return [kw.strip() for kw in kws]


def save_result(directory, keyword, count):
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d')

    dir_path = os.path.join(PWD, directory)
    if not os.path.exists(dir_path):
        print 'Creating directory: %s' % dir_path
        os.mkdir(dir_path)

    path = os.path.join(PWD, directory, keyword)
    print "Save to file: %s" % path

    with file(path, 'a') as result:
        result.write("%s %s\n" % (now_str, count))


def generate_json(data_type, output_file=None):
    path = os.path.join(PWD, data_type)
    output = {}
    for result in os.listdir(path):

        date_count = collections.OrderedDict()

        file_path = os.path.join(PWD, data_type, result)
        data = open(file_path, 'r').readlines()

        for line in data:
            tokens = line.split()
            try:
                date_count[tokens[0]] = float(tokens[1])
            except TypeError:
                pass

        output[result] = date_count.items()

    if output_file is None:
        output_file = '%s.json' % data_type

    with file(os.path.join(PWD, output_file), 'w') as outputfile:
        print "Dumping to %s" % outputfile
        outputfile.write(json.dumps(output))
        outputfile.flush()


def zhilian():
    base_url = 'http://sou.zhaopin.com/jobs/searchresult.ashx?kw=%(kw)s&jl=全国'

    for key in read_keywords():
        url = base_url % {'kw': key}
        print "Fetch page: %s" % url

        while True:
            try:
                response = urllib2.urlopen(url, timeout=8)
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

        data_type = 'zhilian_count'
        save_result(data_type, key, count)

    generate_json(data_type)
    print 'Done'


def update_from_lagou():
    data_type = 'lagou_salary'
    for kw in read_keywords():
        stats = lagou.get_stats(kw)
        save_result(data_type, kw, stats.median)

    generate_json(data_type)


if __name__ == '__main__':
    try:
        zhilian()
    except Exception as ex:
        traceback.print_exc()

    try:
        update_from_lagou()
    except Exception as ex:
        traceback.print_exc()
