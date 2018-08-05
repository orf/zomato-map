from typing import Dict
import requests
import bs4
import tqdm
import os
import asyncio
import aiohttp
import json

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 Firefox/62.0'
start_url = 'https://www.zomato.com/grande-lisboa/lisboa-restaurants?gold_partner=1'

headers = {
    'User-Agent': UA,
    'Accept-Language': 'en-GB',
    'Referer': 'https://www.zomato.com/',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

api_headers = {
    'user-key': os.environ['ZOMATO_KEY']
}

results_per_page = 15

tag_mapping = {
    'https://www.zomato.com//images/red/gold_blue_tag_2_en.png': 'drinks',
    'https://www.zomato.com//images/red/gold_blue_tag_1_en.png': 'food'
}


def scrape_zomato():
    places = {}
    with tqdm.tqdm() as pbar:
        page = 0
        while True:
            pbar.set_postfix_str(f'Page {page}')
            resp = parse_page(f'{start_url}&page={page}')
            if resp is None:
                break
            places.update(extract_results(resp))
            page += 1
            pbar.update(1)

    loop = asyncio.get_event_loop()
    places_with_data = loop.run_until_complete(scrape_api(places))
    with open('zomato_places.json', 'w') as fd:
        json.dump(places_with_data, fd, indent=4, sort_keys=True)


def parse_page(url):
    response = requests.get(url, headers=headers)
    if response.history and response.url.endswith('page=1'):
        return None
    return bs4.BeautifulSoup(response.text, features='lxml')


def extract_results(page: bs4.BeautifulSoup):
    places = page.select('.js-search-result-li')
    for place in places:
        tags = place.select('.red_res_tag img')
        if len(tags) != 1:
            raise RuntimeError(f'Unexpected tags: {tags}')
        src = tags[0]['src']
        if src not in tag_mapping:
            raise RuntimeError(f'Tag {src} not found')

        yield place['data-res_id'], tag_mapping[src]


async def fetch_place_from_api(sesh, id, offer_type):
    async with sesh.get(f'https://developers.zomato.com/api/v2.1/restaurant?res_id={id}', headers=api_headers) as resp:
        res_json = await resp.json()
        res_json['offer_type'] = offer_type
        return res_json


async def scrape_api(places: Dict[str, str]):
    async with aiohttp.ClientSession(raise_for_status=True) as sesh:
        tasks = [
            fetch_place_from_api(sesh, res_id, offer)
            for res_id, offer in places.items()
        ]
        return [
            await f
            for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks))
        ]


if __name__ == '__main__':
    scrape_zomato()
