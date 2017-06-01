# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from forum.items import PostItemsList
import logging
import re, dateparser, time
from bs4 import BeautifulSoup

class CancerForum(CrawlSpider):
    name = 'chroniclymphocyticleukemia_cancerforums_spider'
    allowed_domains = ['cancerforums.net']
    start_urls = ['http://www.cancerforums.net/forums/15-Leukemia-Forum']

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//a[@rel="next"]',canonicalize=True),
             callback="parse_item", follow=True),


        Rule(LinkExtractor(restrict_xpaths='//a[@class="title"]',canonicalize=True),
             callback='parse_item', follow=True),
    )

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text

    def getDate(self,date_str):
        # date_str="Fri Feb 12, 2010 1:54 pm"
        date = dateparser.parse(date_str)
        epoch = int(date.strftime('%s'))
        create_date = time.strftime("%Y-%m-%d'T'%H:%M%S%z",  time.gmtime(epoch))
        return create_date
    
    def parse_item(self, response):
        if "threads" in response.url:
            # little trick for allow use only two rules
            items = []
            condition="breast cancer"
            posts = response.xpath('//ol[@id="posts"]/li')
            url = response.url
            subject = response.xpath(
                '//span[@class="threadtitle"]//text()').extract()[0]
            for post in posts:
                item = PostItemsList()
                author = post.xpath(
                    './/a[contains(@class, "username")]//text()').extract()[0]
                author_link = post.xpath(
                    './/a[contains(@class, "username")]/@href').extract()[0]
                
                create_date = post.xpath(
                    './/span[@class="date"]//text()').extract()
                # clean create_date
                create_date = u" ".join(date.strip() for date in create_date)
                message = post.xpath(
                    './/div[@class="content"]//text()').extract()
                # clean message
                message = u" ".join(msg.strip() for msg in message)
                message = self.cleanText(message)

                item['author'] = author
                item['author_link'] = author_link
                item['condition'] = condition

                create_date = self.getDate(self.cleanText(" ".join(create_date)))
                item['create_date'] = create_date

                item['post'] = self.cleanText(message)
                item['tag'] = ''
                item['topic'] = subject
                item['url'] = url

                logging.info(item.__str__())
                items.append(item)

            return items
