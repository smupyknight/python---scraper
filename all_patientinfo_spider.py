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
    name = "all_patientinfo_spider"
    allowed_domains = ["patient.info"]
    start_urls = [
        "http://patient.info/forums/discuss/browse/epilepsy-801",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//ul[@class="thread-list"]/li//h3/a',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="reply-ctrl-wrap reply-ctrl-last"][last()]',
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
        posts = sel.xpath('//div[@id="topic-replies"]//article[contains(@class,"post")]')
        items = []
        topic = response.xpath('//h1[@class="title"]/text()').extract_first()
        url = response.url
        
        item = PostItemsList()
        item['author'] = response.xpath('//div[@id="topic"]/div[@class="avatar"]/a/p/strong[1]/text()').extract_first()
        item['author_link'] = response.xpath('//div[@id="topic"]/div[@class="avatar"]/a/@href').extract_first()
        item['condition']=topic

        create_date = self.getDate(self.cleanText(" ".join(response.xpath('//div[@id="topic"]//article//time/@datetime').extract_first().strip())))
        item['create_date'] = create_date

        item['post'] = re.sub('\s+',' '," ".join(response.xpath('//div[@id="topic"]//div[@class="post-content break-word"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
        item['tag']=''
        item['topic'] = topic
        item['url']=url
        # logging.info(item.__str__)
        items.append(item)
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('./span[@class="post-username"]/a/text()').extract_first()
            item['author_link'] = post.xpath('./span[@class="post-username"]/a/@href').extract_first()
            item['condition']=topic

            create_date = self.getDate(self.cleanText(" ".join(post.xpath('.//time/@datetime').extract_first())))
            item['create_date'] = create_date

            item['post'] = re.sub('\s+',' '," ".join(post.xpath('./div[@class="post-content break-word"]/p/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
            item['tag']=''
            item['topic'] = topic
            item['url']=url
            # logging.info(item.__str__)
            items.append(item)
        return items
