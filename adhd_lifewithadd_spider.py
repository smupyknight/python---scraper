import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
from bs4 import BeautifulSoup
import logging, dateparser, time

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "adhd_lifewithadd_spider"
    allowed_domains = ["www.lifewithadd.org"]
    start_urls = [
        "http://www.lifewithadd.org/forum/categories/general/listForCategory",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="xg_module_body"]//h3/a',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//ul[@class="pagination easyclear "]/li[last()-1]/a',
                    canonicalize=True,
                ), follow=True),
        )

    def getDate(self,date_str):
        # date_str="Fri Feb 12, 2010 1:54 pm"
        date = dateparser.parse(date_str)
        epoch = int(date.strftime('%s'))
        create_date = time.strftime("%Y-%m-%d'T'%H:%M%S%z",  time.gmtime(epoch))
        return create_date

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//dl[@class="discussion clear i0 xg_lightborder"]')
        items = []
        
        topic = response.xpath('//h1/text()').extract_first()
        url = response.url
        condition="adhd"
        item = PostItemsList()
        item['author'] = response.xpath('//div[@class="xg_module xg_module_with_dialog"]//ul[@class="navigation byline"]/li/a[contains(@href,"profile")]/text()').extract_first()
        item['author_link'] = response.xpath('//div[@class="xg_module xg_module_with_dialog"]//ul[@class="navigation byline"]/li/a[contains(@href,"profile")]/@href').extract_first()
        item['condition']=condition

        create_date = self.getDate(self.cleanText(" ".join(response.xpath('//div[@class="xg_module xg_module_with_dialog"]//ul[@class="navigation byline"]/li/a[@class="nolink"][2]/text()').extract_first().replace('on','').replace('in','').strip())))
        item['create_date'] = create_date

        item['post'] = re.sub('\s+',' '," ".join(response.xpath('//div[@class="xg_module xg_module_with_dialog"]//div[@class="xg_user_generated"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
        if not item['post']:
            item['post'] = re.sub('\s+',' '," ".join(response.xpath('//div[@class="xg_module xg_module_with_dialog"]//div[@class="xg_user_generated"]/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
        item['tag']=condition
        item['topic'] = topic
        item['url']=url
        logging.info(item.__str__)
        items.append(item)
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('./dt[@class="byline"]/a[contains(@href,"user")]/text()').extract_first()
            item['author_link'] = post.xpath('./dt[@class="byline"]/a[contains(@href,"user")]/@href').extract_first()
            item['condition']=condition

            create_date = self.getDate(self.cleanText(" ".join(post.xpath('./dt[@class="byline"]/span[@class="timestamp"]/text()').extract_first())))
            item['create_date'] = create_date

            item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="description"]/div[@class="xg_user_generated"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
            if not item['post']:
                item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="description"]/div[@class="xg_user_generated"]/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
            item['tag']=condition
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
