
from settings import *

redisClient = redisCli()
if redisClient.get_status() != 'running': first_job()

import asyncio
import template
import aiohttp
from bs4 import BeautifulSoup
from multiprocessing import Process

redisClient = redisCli()

procersses = []

redisClient.start_crawling()

conn = aiohttp.TCPConnector(limit_per_host=100, limit=0, ttl_dns_cache=300)

def process_page(page):
    doc = BeautifulSoup(page['content'], 'html.parser')
    fun_to_call = getattr(template, page['call_back'])
    result = fun_to_call(doc)
    if 'data' in result.keys() and len(result['data']):
        redisClient.redis_push('data', result['data'])
    if 'url' in result.keys() and len(result['url']):
        for job in result['url']:
            redisClient.redis_push('job_queue', job)

async def extracting():
    while redisClient.get_status() == 'running':
        job_left = (redisClient.length_of_queue('job_queue'))
        page_left = (redisClient.length_of_queue('page_queue'))
        if page_left:
            page = redisClient.redis_pop('page_queue')
            redisClient.incr_process_count()
            process_page(page)
            redisClient.dicr_process_count()
        await asyncio.sleep(.1)

async def fetching():

    semaphore = asyncio.Semaphore(50)
    session = aiohttp.ClientSession(connector=conn)
    
    async def push_page(job):
        url = job['url']
        redisClient.incr_process_count()
        async with semaphore:
            async with session.get(url, ssl=False) as response:
                doc = await response.text()
                redisClient.redis_push('page_queue', {'content':doc, 'call_back':job['call_back']})
                redisClient.dicr_process_count() 

    while redisClient.get_status() == 'running':
        job_left = (redisClient.length_of_queue('job_queue'))
        page_left = (redisClient.length_of_queue('page_queue'))
        if job_left:
            asyncio.create_task(push_page(redisClient.redis_pop('job_queue')))
        await asyncio.sleep(0.5)

    # await session.close()  

async def main():
    
    fetching_routine = asyncio.ensure_future(fetching())
    extracting_routine = asyncio.ensure_future(extracting())
    quit()
    
    while redisClient.get_status() == 'running':

        await asyncio.sleep(1)
        if redisClient.length_of_queue('job_queue') == 0 and redisClient.length_of_queue('page_queue') == 0:
            if redisClient.get_process_count() == '0':
                redisClient.stop_crawling()

        job_len = redisClient.length_of_queue('job_queue')
        page_len = redisClient.length_of_queue('page_queue')
        data_len = redisClient.length_of_queue('data')
        state = redisClient.get_status()
        count = redisClient.get_process_count()
        print(f'job_len:{job_len} page_len:{page_len} count:{count} data_len:{data_len} state:{state}')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())



    # import pdb; pdb.set_trace()
