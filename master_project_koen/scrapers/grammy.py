# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Spider
import datetime
from lxml import html
import requests


class GrammySpider(Spider):
    name = 'grammy'

    def __init__(self, *args, **kwargs):
        self.headers = {
            'authority': 'www.grammy.com',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.grammy.com/grammys/awards/39th-annual-grammy-awards-1996',
            'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
            'cookie': 'has_js=1; USERCONSENT=2; _ga=GA1.2.1065152189.1621335304; __qca=P0-1068909896-1621335304859; _parsely_session={%22sid%22:5%2C%22surl%22:%22https://www.grammy.com/grammys/awards/18th-annual-grammy-awards-1975%22%2C%22sref%22:%22https://www.grammy.com/grammys/awards/63rd-annual-grammy-awards-2020%22%2C%22sts%22:1621973608183%2C%22slts%22:1621551187272}; _parsely_visitor={%22id%22:%2259b02f13-5ae2-4a66-bdfa-057d2d616386%22%2C%22session_count%22:5%2C%22last_session_ts%22:1621973608183}; _gid=GA1.2.373702483.1621973609; AMP_TOKEN=%24NOT_FOUND; RT="z=1&dm=grammy.com&si=5dde7e8c-1faa-4a81-901c-49fc622c3ab0&ss=kp4huk9i&sl=4&tt=ex6&bcn=%2F%2F684d0d36.akstat.io%2F&ld=9dxr"',
            'if-none-match': '"1621971409-1"',
            'if-modified-since': 'Tue, 25 May 2021 19:36:49 GMT',
        }

        super(GrammySpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        """
        This method yields the urls of grammy awards
        """
        # getting start urls
        content = requests.get('https://www.grammy.com/grammys/awards/2nd-annual-grammy-awards-1958').content
        tree = html.fromstring(content)

        paths = tree.xpath('//a[contains(text(), "Annual GRAMMY")]/@href')

        for p in paths:
            yield scrapy.Request(
                url=f'https://www.grammy.com/{p}',
                callback=self.parse,
                headers=self.headers,

            )

    def parse(self, response):
        """
        This method gets detail page and parse the data
        """
        all_page_data = []
        categories = response.xpath('//div[@class="view-grouping"]')

        for cat in categories:
            cat_songs = []
            cat_name = cat.xpath('.//div[@class="view-grouping-header"]/text()').get()
            winners = cat.xpath(
                './/div[contains(@class,"views-row views-row-1 views-row-odd views-row-first views-row-last group- group-winner")]//div[@class="wrapper views-fieldset"]')
            for win in winners:
                name = win.xpath('./div[@class="views-field views-field-title"]//text()').get()
                artists = win.xpath('./div[@class="views-field views-field-field-description"]//text()').getall()
                if artists:
                    artists = (', '.join(artists)).strip()
                if not artists:
                    artists = None

                cat_songs.append({
                    'status': 'winner',
                    'name': name,
                    'artists': artists
                })

            nominees = cat.xpath('.//div[contains(@class,"group-nominees group-")]')
            for nom in nominees:
                name = nom.xpath('.//div[@class="views-field views-field-title"]//text()').get()
                artists = nom.xpath('.//div[@class="views-field views-field-field-description"]//text()').getall()
                if artists:
                    artists = (', '.join(artists)).strip()
                if not artists:
                    artists = None

                cat_songs.append({
                    'status': 'nominee',
                    'name': name,
                    'artists': artists
                })

            all_page_data.append({
                'category': cat_name,
                'songs': cat_songs
            })
        yield {
            'url': response.url,
            'data': all_page_data

        }
