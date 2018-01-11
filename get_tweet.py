# -*- coding: utf-8 -*-
import json
from requests_oauthlib import OAuth1Session
import config as con
import time, datetime

try:
    import argparse

    parser = argparse.ArgumentParser(description='Twitter python client')
except ImportError:
    parser = None


def get_line(twitter, url, num):
    """
    get time line
    :param twitter:OAuth Session
    :param url: Connect API URL
    :param num: Tweet Num
    :return: Tweet Data
    """
    available_reqcnt_limit = None
    reset_reqlimit_utc = None
    reset_reqlimit_sec = None
    datalist = []

    params = {'count': 200}
    # Twitter API Get Timeline
    res = twitter.get(url, params=params)

    if res.status_code == 200:
        timelines = json.loads(res.text)

        # 15min 15 cnt Limit
        # Available Request Lim Count
        available_reqcnt_limit = res.headers['x-rate-limit-remaining']
        # Reset Request Lim Count(UTC)
        reset_reqlimit_utc = res.headers['x-rate-limit-reset']
        # Mod UTC -> Sec
        reset_reqlimit_sec = int(res.headers['X-Rate-Limit-Reset']) - time.mktime(datetime.datetime.now().timetuple())

        for user_tweet in timelines:
            datalist.append((
                user_tweet['user']['name'] + ":@" + user_tweet['user']['screen_name'],
                user_tweet['text'],
                "https://twitter.com/statuses/" + user_tweet['id_str'],
                user_tweet['favorite_count'],
                user_tweet['retweet_count'],
                user_tweet['created_at']
            ))

    elif res.status_code == 429:
        print('Service Unavailable 429')
        time.sleep(reset_reqlimit_utc)

        if available_reqcnt_limit == 0:
            raise Exception('Error %d' % res.status_code)

    elif res.status_code == 503:
        print('Service Unavailable 503')
        time.sleep(reset_reqlimit_sec)

        if available_reqcnt_limit == 0:
            raise Exception('Error %d' % res.status_code)
    else:
        print("Failed: %d" % res.status_code)

    return datalist, available_reqcnt_limit, reset_reqlimit_utc, reset_reqlimit_sec


def main(path, flg):
    # write config.py Twitter API Key
    CK = con.CONSUMER_KEY
    CS = con.CONSUMER_SECRET
    AT = con.ACCESS_TOKEN
    ATS = con.ACCESS_TOKEN_SECRET

    twitter = OAuth1Session(CK, CS, AT, ATS)

    # Get TimeLine
    api_url = "https://api.twitter.com/1.1/"
    url = api_url + "statuses/home_timeline.json"
    data, limit, reset, sec = get_line(twitter, url, 1000)

    if len(data) > 0:
        if flg == 1:
            # Fav Sort
            sdata = sorted(data, reverse=True, key=lambda x: x[3])
        else:
            # RT Sort
            sdata = sorted(data, reverse=True, key=lambda x: x[4])

        with open(path, "w") as f:
            f.write(str(limit) + " -> ")
            f.write("WAIT(sec):" + str(sec) + "\n")
            f.write("#" * 10 + "\n")
            for v in sdata:
                f.write(v[0] + "\n")
                f.write(v[1] + "\n")
                f.write(v[2] + "\n")
                f.write(str(v[3]) + ",")
                f.write(str(v[4]) + ",")
                f.write(str(v[5]) + "\n")
                f.write("-" * 10 + "\n")


if __name__ == '__main__':
    parser.add_argument('--file', default=None, help="VIM BufferTmpFile Path")
    parser.add_argument('--flg', default=1, help="1:Fav Sort x:RT Sort")
    args = parser.parse_args()
    if args.file is None:
        # print("Error")
        main("/tmp/vim_tmp_buf.text")
    else:
        main(args.file, args.flg)
