from multiprocessing import Pool
from time import sleep


def job(url):
    sleep(3)
    print(url)


def job_multi():
    pool = Pool(100)
    urls = range(100)
    pool.map(job, urls)


if __name__ == '__main__':
    job_multi()
