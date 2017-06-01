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
    name = "breastcancer_bcausorg_spider"
    allowed_domains = ["bcaus.org.au"]
    start_urls = [
        "http://www.bcaus.org.au/phpBB3/index.php",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="topictitle"]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="forumlink"]',
                    canonicalize=True,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),
            Rule(LinkExtractor(
                    restrict_xpaths='//a[contains(@href,"viewforum.php?")]',
                    canonicalize=True,
                    deny=(r'user_profile_*\.html',)
                ), follow=True),
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

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//table[@class="tablebg"]')
        items = []
        topic = response.xpath('//h2//text()').extract()[0]
        url = response.url
        condition="breast cancer"
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//b[@class="postauthor"]/text()').extract()[0]
            item['author_link'] = post.xpath('.//a[contains(@href,"viewprofile")]/@href').extract()[0]
            item['condition'] = condition

            create_date = self.getDate(self.cleanText(" ".join(post.xpath('.//div[contains(.//text(),"Posted")]/text()').extract())))
            item['create_date'] = create_date
           
            message = ''.join(post.xpath('.//div[@class="postbody"]/text()').extract())
            item['post'] = self.cleanText(message)
            item['tag']='breastcancer'
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items
