import logging
import random
import time
import requests
from bs4 import BeautifulSoup
from spiders.configs import log_path, error_list_path, host_url


def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(file_handler)
    l.addHandler(stream_handler)


class TimeInterval:
    call_count = 0

    def __init__(self, download_interval=5, rest_interval=60, rest_freq=100):
        self._download_interval = download_interval
        self._rest_interval = rest_interval
        self._rest_freq = rest_freq

    def get_interval(self):
        if self.call_count <= self._rest_freq:
            self.call_count += 1
            if self._download_interval <= 2:
                return 0
            else:
                return random.randint(self._download_interval - 2, self._download_interval + 2)
        else:
            self.call_count = 0
            return random.randint(self._rest_interval - 20, self._rest_interval + 20)


User_Agents = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0b8) Gecko/20100101 Firefox/4.0b8',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_5_8) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.68 Safari/534.24',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_4) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.100 Safari/534.30',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_6) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.12 Safari/534.24',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_6) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.698.0 Safari/534.24',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_7) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.68 Safari/534.24',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.0 Safari/534.24',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X; U; en; rv:1.8.0) Gecko/20060728 Firefox/1.5.0 Opera 9.27',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-GB; rv:1.9.0.6) Gecko/2009011912 Firefox/3.0.6',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.10) Gecko/2009122115 Firefox/3.0.17',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.6) Gecko/2009011912 Firefox/3.0.6',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1b3pre) Gecko/20090204 Firefox/3.1b3pre',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1b4) Gecko/20090423 Firefox/3.5b4 GTB5',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; fr; rv:1.9.1b4) Gecko/20090423 Firefox/3.5b4',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; it; rv:1.9b4) Gecko/2008030317 Firefox/3.0b4',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; ko; rv:1.9.1b2) Gecko/20081201 Firefox/3.1b2',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
]

# for production
# time_interval = TimeInterval(download_interval, rest_interval, rest_freq)
# for test
time_interval = TimeInterval(download_interval=2)

setup_logger('prj_logger', log_path)
setup_logger('error_list', error_list_path)
prj_logger = logging.getLogger('prj_logger')
error_list_logger = logging.getLogger('error_list')

http_proxy = "http://127.0.0.1:8086/"
https_proxy = "http://127.0.0.1:8086/"

proxy_dict = {
    "http": http_proxy,
    "https": https_proxy,
}


def get_random_user_agent():
    return random.choice(User_Agents)


def get_headers():
    headers = {
        'User-Agent': get_random_user_agent(),
        'Referer': host_url
    }
    return headers


def get_soup_from_url(url, add_host_url=True):
    if add_host_url:
        url = host_url + url
    # time.sleep(time_interval.get_interval())
    prj_logger.info('Visiting: {}'.format(url))
    try:
        wb_data = requests.get(url, headers=get_headers(), proxies=proxy_dict, verify=False, timeout=5)
    except:
        time.sleep(40)
        wb_data = requests.get(url, headers=get_headers(), proxies=proxy_dict, verify=False, timeout=5)
    wb_data.encoding = 'utf8'
    if wb_data.status_code == 404:
        return None
    soup = BeautifulSoup(wb_data.text, 'html5lib')
    return soup


# def get_soup_from_url(url, add_host_url=True):
#     # fn = "D:\Downloads\single.html"
#     fn = "D:\Downloads\listnum.html"
#     with open(fn, encoding='utf-8') as f:
#         soup = BeautifulSoup(f.read(), 'html5lib')
#         return soup


if __name__ == '__main__':
    print(get_soup_from_url(host_url, False))
