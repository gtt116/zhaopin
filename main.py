#-*-coding:utf-8-*-
import os
import sys
PWD = os.path.dirname(__file__)
sys.path.insert(0, PWD)

import traceback
import time
import urllib2

from bs4 import BeautifulSoup as BS
import influx


DB = None


def read_keywords():
    filepath = os.path.join(PWD, 'keywords.txt')
    kws = file(filepath, 'r').readlines()
    return [kw.strip() for kw in kws]


def save_to_influx(directory, keyword, count):
    global DB
    if DB is None:
        DB = influx.InfluxDB('zhaopin')
    DB.write_point(directory, keyword, count)


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
            save_to_influx(data_type, key, count)

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
        return 'http://sou.zhaopin.com/jobs/searchresult.ashx?kw=%(kw)s&jl=全国&sm=0' % {'kw': key}

    def get_data_type(self):
        return 'zhilian_count'

    def get_response(self, url):
        req = urllib2.Request(url)
        req.add_header(
            'user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko)'
        )
        response = urllib2.urlopen(req, timeout=8)
        return response

    def get_job_count(self, body):
        bs = BS(body, "html.parser")
        em = bs.find('span', class_="search_yx_tj").find('em')
        count = em.string
        return count


class Job51(JobCounter):

    def get_url(self, key):
        url = 'http://search.51job.com/jobsearch/search_result.php?fromJs=1&jobarea=000000%2C00&funtype=0000&industrytype=00&keyword={0}&keywordtype=2&lang=c&stype=2&postchannel=0000&fromType=1&confirmdate=9'.format(key)
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


def main():
    try:
        Job51().run()
    except Exception as ex:
        traceback.print_exc()

    try:
        Zhilian().run()
    except Exception as ex:
        traceback.print_exc()


if __name__ == '__main__':
    main()

