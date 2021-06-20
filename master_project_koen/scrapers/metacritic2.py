# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Spider


class MetacriticSpider(Spider):
    name = 'metacritic1'

    def __init__(self, *args, **kwargs):
        self.headers = {
            'authority': 'www.metacritic.com',
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

        super(MetacriticSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        """
        This method yields the listing urls with pagination
        """
        for page_number in range(0, 128):
            yield scrapy.Request(
                url=f'https://www.metacritic.com/browse/albums/score/metascore/all/filtered?sort=desc&page={page_number}',
                callback=self.parse,
                headers=self.headers)

    def parse(self, response):
        """
        This method gets listing page and follow the detail(result) pages
        """
        results_urls = response.xpath('//a[@class="title"]/@href')

        for url in results_urls:
            absoulte_url = 'https://www.metacritic.com' + url.get()
            yield scrapy.Request(
                url=absoulte_url,
                callback=self.parse_detail_page,
                headers=self.headers)

    def parse_detail_page(self, response):
        """
        This method parse detail page
        """
        title = response.xpath('//div[@class="product_title"]//span[@itemprop="name"]/h1/text()').get()
        artist = response.xpath('//div[@class="product_artist"]//span[@class="band_name"]/text()').get()
        date_published = response.xpath('//div[@class="product_data"]//span[@itemprop="datePublished"]/text()').get()
        summary = response.xpath('//div[@class="section product_details"]//span[@itemprop="description"]/text()').get()
        meta_score = response.xpath('//span[@itemprop="ratingValue"]/text()').get()
        user_score = response.xpath('(//div[contains(@class,"metascore_w user large album")])[1]/text()').get()
        genre = response.xpath('//span[@itemprop="genre"]/text()').get()

        data = {
            'url': response.url,
            'title': title,
            'artist': artist,
            'datePublished': date_published,
            'summary': summary.strip() if summary else summary,
            'meta_score': meta_score,
            'user_score': user_score,
            'genre': genre,
            'critic-reviews': []

        }
        yield scrapy.Request(
            url=response.url + '/critic-reviews',
            callback=self.parse_critic_review,
            headers=self.headers,
            meta={'data': data})

    def parse_critic_review(self, response):
        """
        This method parses critic review page and get the reviews, append previous data and go for user reviews
        """
        data = response.meta['data']

        reviews_obj = data['critic-reviews']
        reviews = response.xpath('//ol[@class="reviews critic_reviews"]/li[contains(@class, "review critic_review")]')

        for r in reviews:
            reviews_obj.append(
                {
                    'score': r.xpath('.//div[@class="review_grade"]/div/text()').get(),
                    'reviewer': r.xpath('.//div[@class="source"]//text()').get(),
                    'date_published': r.xpath('.//div[@class="date"]//text()').get(),
                    'review_body': (r.xpath('.//div[@class="review_body"]//text()').get()).strip(),
                }
            )

        data.update({
            'critic-reviews': reviews_obj,
            'user_reviews': []
        })
        # pagination of critic reviews
        nex_page = response.xpath('//span[@class="flipper next"]/a/@href').get()
        if nex_page:
            yield scrapy.Request(
                url='https://www.metacritic.com' + nex_page,
                callback=self.parse_critic_review,
                headers=self.headers,
                meta={'data': data})

        if not nex_page:
            yield scrapy.Request(
                url=data['url'] + '/user-reviews',
                callback=self.parse_user_review,
                headers=self.headers,
                meta={'data': data})

    def parse_user_review(self, response):
        """
        This method parses user review page and append previous data and yield the data
        """

        data = response.meta['data']

        reviews_obj = data['user_reviews']
        reviews = response.xpath('//ol[@class="reviews user_reviews"]/li[contains(@class, "review user_review")]')

        for r in reviews:
            reviews_obj.append(
                {
                    'score': r.xpath('.//div[@class="review_grade"]/div/text()').get(),
                    'reviewer': (''.join(r.xpath('.//div[@class="name"]//text()').getall())).strip(),
                    'date_published': r.xpath('.//div[@class="date"]//text()').get(),
                    'review_body': ''.join(r.xpath('.//div[@class="review_body"]//text()').getall()).replace('Expand',
                                                                                                             '').strip(),
                    'helpul_count': r.xpath('.//span[@class="total_ups"]/text()').get(),
                }
            )

        data.update({
            'user_reviews': reviews_obj,
        })
        # pagination of user reviews
        nex_page = response.xpath('//span[@class="flipper next"]/a/@href').get()
        if nex_page:
            yield scrapy.Request(
                url='https://www.metacritic.com' + nex_page,
                callback=self.parse_user_review,
                headers=self.headers,
                meta={'data': data})

        if not nex_page:
            yield data
