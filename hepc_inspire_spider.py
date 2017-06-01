#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging, dateparser, time
from bs4 import BeautifulSoup
# import lxml.html
# from lxml.etree import ParserError
# from lxml.cssselect import CSSSelector

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "carcinoidcancer_inspire_spider"
    allowed_domains = ["inspire.com"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://ehealthforum.com/health/hepatitis_c.html",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//*[@id="search-results"]/h3',
                canonicalize=True,
                ), callback='parsePost', follow=True),

            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                restrict_xpaths='//div[contains(@class, "pagination-home")]',
                canonicalize=True,
                #allow='http://www.cancerforums.net/threads/',
            ), follow=True),
            Rule(LinkExtractor(
                restrict_xpaths='//div[contains(@class, "pagination")]',
                canonicalize=True,
                #allow='http://www.cancerforums.net/threads/',
            ), callback='parsePost', follow=True),
        )

    def getDate(self,date_str):
        # date_str="Fri Feb 12, 2010 1:54 pm"
        date = dateparser.parse(date_str)
        epoch = int(date.strftime('%s'))
        create_date = time.strftime("%Y-%m-%d'T'%H:%M%S%z",  time.gmtime(epoch))
        return create_date

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        condition="hep c"
        posts = sel.css('.comments-box')
        items = []
        topic = sel.css('.post-title').xpath('./text()').extract()[0].strip()
        url = response.url

        item = PostItemsList()
        item['author'] = self.parseText(str=sel.css('.content-primary-post').xpath('./div[1]/ul/li[1]/a').extract()[0].strip())
        item['author_link']=response.urljoin(sel.css('.content-primary-post').xpath('./div[1]/ul/li[1]/a/@href').extract()[0])
        item['condition']=condition

        create_date = self.getDate(self.cleanText(" ".join(self.parseText(sel.css('.content-primary-post').xpath('./div[1]/ul/li[1]/text()').extract()[1].split('\n')[1].strip()[1:]))))
        item['create_date'] = create_date

        post_msg=self.parseText(str=sel.css('.content-primary-post').xpath('./div[2]/p').extract()[0])
        item['post']=post_msg
        item['tag']=''
        item['topic'] = topic
        item['url']=url
        logging.info(post_msg)
        items.append(item)

        for post in posts:
            if len(post.css('.post-info'))==0:
                continue
            item = PostItemsList()
            item['author'] = self.parseText(str=post.css('.post-info').xpath('./ul/li[1]/a').extract()[0].strip())
            item['author_link']=response.urljoin(post.css('.post-info').xpath('./ul/li[1]/a/@href').extract()[0])
            item['condition']=condition

            create_date = self.getDate(self.cleanText(" ".join(self.parseText(str=post.css('.post-info').xpath('./ul/li[3]').extract()[0]))))
            item['create_date'] = create_date

            post_msg=self.parseText(str=post.xpath('./p').extract()[0])
            item['post']=post_msg
            item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(post_msg)
            items.append(item)
        return items

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()
