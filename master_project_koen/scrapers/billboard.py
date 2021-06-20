# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Spider
import datetime


class BillboardSpider(Spider):
    name = 'billboard'

    def __init__(self, *args, **kwargs):
        self.headers = {
            'authority': 'www.billboard.com',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9,ru;q=0.8'
        }

        super(BillboardSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        """
        This method yields the urls from date 1963-07-17 to the current date with one week difference
        """

        today_date = datetime.datetime.now().date()
        start_date = datetime.date(1963, 7, 17)
        week_no = 0
        while True:
            next_date = datetime.timedelta(weeks=week_no)
            new_date = start_date + next_date
            yield scrapy.Request(
                url=f'https://www.billboard.com/charts/billboard-200/{new_date.__str__()}',
                callback=self.parse,
                headers=self.headers,
                meta={'date': new_date.__str__()}

            )
            week_no = week_no + 1
            if new_date > today_date:
                break

    def parse(self, response):
        """
        This method gets detail page and parse the data
        """
        date = response.meta['date']
        songs_data = response.xpath('//li[@class="chart-list__element display--flex"]')
        songs_per_date = []
        for s in songs_data:
            songs_per_date.append(
                {
                    'position': s.xpath('.//span[@class="chart-element__rank__number"]/text()').get(),
                    'title': s.xpath('.//span[@class="chart-element__information__song text--truncate color--primary"]/text()').get(),
                    'artist': s.xpath('.//span[@class="chart-element__information__artist text--truncate color--secondary"]/text()').get(),
                    'last_week': s.xpath('.//span[@class="chart-element__meta text--center color--secondary text--last"]/text()').get(),
                    'peak': s.xpath('.//span[@class="chart-element__meta text--center color--secondary text--peak"]/text()').get(),
                    'week': s.xpath('.//span[@class="chart-element__meta text--center color--secondary text--week"]/text()').get(),
                }
            )

        yield {
            'date': date,
            'songs': songs_per_date
        }

