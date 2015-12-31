#-*-coding:utf-8-*-
import os
import sys
PWD = os.path.dirname(__file__)
# After this, we can import module lagou from any workspace
sys.path.insert(0, PWD)

import traceback
import time
import urllib2
import urllib
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


class JobCounter(object):

    def run(self):

        for key in read_keywords():
            url = self.get_url(key)
            print "Fetch page: %s" % url

            while True:
                try:
                    response = self.get_response(url)
                    body = response.read()
                except Exception as ex:
                    print ex
                    print 'retry after 1 second'
                    time.sleep(1)
                else:
                    break

            count = self.get_job_count(body)
            print "Found count: %s" % count

            data_type = self.get_data_type()
            save_result(data_type, key, count)

        generate_json(data_type)
        print 'Done'

    def get_data_type(self):
        raise NotImplementedError()

    def get_url(self, key):
        raise NotImplementedError()

    def get_response(self, url):
        raise NotImplementedError()

    def get_job_count(self, body):
        raise NotImplementedError()


class Zhilian(JobCounter):

    def get_url(self, key):
        return 'http://sou.zhaopin.com/jobs/searchresult.ashx?kw=%(kw)s&jl=全国' % {'kw': key}

    def get_data_type(self):
        return 'zhilian_count'

    def get_response(self, url):
        return urllib2.urlopen(url, timeout=8)

    def get_job_count(self, body):
        bs = BS(body, "html.parser")
        em = bs.find('span', class_="search_yx_tj").find('em')
        count = em.string
        return count


class Job51(JobCounter):

    def get_url(self, key):
        key = urllib.quote(key)
        url = 'http://search.51job.com/list/%2B,%2B,%2B,%2B,%2B,%2B,{0},2,%2B.html?lang=c&stype=1&image_x=53&image_y=9'.format(key)
        return url

    def get_data_type(self):
        return 'job51_count'

    def get_response(self, url):
        req = urllib2.Request(url)
        req.add_header(
            'Cookie', 'guid=145157308952880058; search=jobarea%7E%60000000%7C%21ord_field%7E%600%7C%21list_type%7E%600%7C%21; guide=1'
        )
        response = urllib2.urlopen(req, timeout=8)
        return response

    def get_job_count(self, body):
        bs = BS(body, "html.parser")
        return bs.find('input', attrs={'name': 'jobid_count'})['value']


def update_from_lagou():
    data_type = 'lagou_salary'
    data_type2 = 'lagou_salary_mode'
    data_type3 = 'lagou_count'
    for kw in read_keywords():
        stats = lagou.get_stats(kw)
        save_result(data_type, kw, stats.median)
        save_result(data_type2, kw, stats.mode)
        save_result(data_type3, kw, stats.count)

    generate_json(data_type)
    generate_json(data_type2)
    generate_json(data_type3)


if __name__ == '__main__':
    try:
        Zhilian().run()
    except Exception as ex:
        traceback.print_exc()

    try:
        Job51().run()
    except Exception as ex:
        traceback.print_exc()

    try:
        update_from_lagou()
    except Exception as ex:
        traceback.print_exc()
