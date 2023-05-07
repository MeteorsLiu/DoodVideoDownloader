# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import string
import re
import random
import time

import asyncio
import concurrent.futures
import functools
import os
headers = {
  'authority': 'dood.yt' ,
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' ,
  'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh-MO;q=0.7,zh;q=0.6' ,
  'cookie': 'file_id=5833388; aff=588; ref_url=; lang=1; referer=' ,
  'referer': 'https://dood.yt/e/9rxaw9lq89439wy1bvb49727183d9z1' ,
  'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"' ,
  'sec-ch-ua-mobile': '?0' ,
  'sec-ch-ua-platform': '"Windows"' ,
  'sec-fetch-dest': 'document' ,
  'sec-fetch-mode': 'navigate' ,
  'sec-fetch-site': 'same-origin' ,
  'upgrade-insecure-requests': '1' ,
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36' 
}


async def get_size(url):
    response = requests.head(url, headers=headers)
    size = int(response.headers['Content-Length'])
    return size


def download_range(url, start, end, output):
    h = {
        'authority': 'dood.yt',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh-MO;q=0.7,zh;q=0.6',
        'cookie': 'referer=; lang=1',
        'referer': 'https://dood.yt/',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'Range': f'bytes={start}-{end}'
    }
    response = requests.get(url, headers=h)

    with open(output, 'wb') as f:
        for part in response.iter_content(1024):
            f.write(part)


async def download(run, loop, url, output, chunk_size=1000000):
    file_size = await get_size(url)
    chunks = range(0, file_size, chunk_size)

    tasks = [
        run(
            download_range,
            url,
            start,
            start + chunk_size - 1,
            f'{output}.part{i}',
        )
        for i, start in enumerate(chunks)
    ]

    await asyncio.wait(tasks)

    with open(output, 'wb') as o:
        for i in range(len(chunks)):
            chunk_path = f'{output}.part{i}'

            with open(chunk_path, 'rb') as s:
                o.write(s.read())

            os.remove(chunk_path)


def getURLLink(url):
    content = requests.get(url, headers=headers).content.decode('utf-8')
    print(content)
    link = re.search(
        r'''(\/pass_md5\/.*)', function\(data\)''', content).group(1)
    token = re.search(
        r'''a\+\"\?token=(.*)&expiry=\"\+Date\.now\(\);};''', content).group(1)
    rlink = requests.get('https://dood.yt' + link,
                         headers=headers).content.decode('utf-8')
    video = rlink + ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
                            for _ in range(10)) + "?token=" + token + "&expiry=" + str(int(time.time()))
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)
    loop = asyncio.new_event_loop()
    run = functools.partial(loop.run_in_executor, executor)
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(
            download(run, loop, video, "t.mp4")
        )
    finally:
        loop.close()



