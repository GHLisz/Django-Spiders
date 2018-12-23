import os
import shutil
import traceback
import time
import json
from multiprocessing.pool import ThreadPool
from datetime import datetime

import requests

CENTER_URL = ''
LOCAL_CACHE = ''

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Referer': ''
}


def get_jobs():
    jobs = requests.get(CENTER_URL, timeout=30)
    jobs = jobs.json()['jobs']
    # print(*jobs, sep='\n')
    return jobs


def down_file(src, dst):
    # print(f'saving {src} to {dst}')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    name = src.split('/')[-1].split('.')[0]
    print(datetime.now(), name)

    r = requests.get(src, stream=True, headers=headers, timeout=1800)
    if r.status_code == 200:
        with open(dst, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def down_file_checked(src, dst, min_size_k):
    down_file(src, dst)
    target_file = dst

    if not os.path.exists(target_file):
        return False

    size_kb = os.stat(target_file).st_size / 1024
    if size_kb > min_size_k:
        return True
    else:
        os.remove(target_file)
        return False


def down_file_repeat(src, dst, min_size_k, repeat_times):
    for _ in range(repeat_times):
        if down_file_checked(src, dst, min_size_k):
            return True
    return False


def report_job_status(failed_jobs, passed_jobs):
    params = {
        'success': True,
        'failed_jobs': failed_jobs,
        'passed_jobs': passed_jobs,
    }
    resp = requests.post(CENTER_URL, data=json.dumps(params))
    print(datetime.now(), 'report resp is: ', resp.text)


def down_helper(jobs):
    unfinished_jobs = list(filter(lambda x: not os.path.exists(x['dst']), (j for j in jobs)))

    jobs_src = [j['src'] for j in unfinished_jobs]
    jobs_local_name = [LOCAL_CACHE + src.split('/')[-1] for src in jobs_src]
    jobs_dst = [j['dst'] for j in unfinished_jobs]

    print('len of job: ', len(jobs_dst))

    # d_f = lambda s, d: down_file_repeat(s, d, 10, 5)
    # with ThreadPool(20) as p:
    #     p.starmap(d_f, zip(jobs_src, jobs_local_name))

    for s, d in zip(jobs_src, jobs_local_name):
        down_file_repeat(s, d, 10, 5)

    failed_jobs, passed_jobs = [], []
    for l, r, s in zip(jobs_local_name, jobs_dst, jobs_src):
        if os.path.exists(l):
            passed_jobs.append(s)
            os.makedirs(os.path.dirname(r), exist_ok=True)
            shutil.move(l, r)
        else:
            failed_jobs.append(s)
            continue
    return failed_jobs, passed_jobs


def main():
    jobs = get_jobs()
    failed_jobs, passed_jobs = down_helper(jobs)
    report_job_status(failed_jobs, passed_jobs)


if __name__ == '__main__':
    os.system(r'net use \\111 "111" /user:"111"')
    os.makedirs(LOCAL_CACHE, exist_ok=True)

    error_count = 0
    while True:
        try:
            main()
        except Exception as e:
            print(datetime.now())
            error_count += 1
            traceback.print_exc()
            time.sleep(5 * error_count)
