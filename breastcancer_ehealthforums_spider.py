import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re, dateparser, time
from bs4 import BeautifulSoup
import logging

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "breastcancer_ehealthforums_spider"
    allowed_domains = ["ehealthforum.com"]
    start_urls = [
        "http://ehealthforum.com/health/breast_cancer.html",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[contains(@class,"topictitle")]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="pagination_number"]',
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
        posts = sel.xpath("//div[@class='fp_left']")
        items = []
        topic = response.xpath("//div[@class='fp_topic_content_title']/text()").extract_first()
        url = response.url
        condition="breast cancer"
        for post in posts:
            item = PostItemsList()
            item['author'] = post.css('a.fp_topic_author').xpath("./span/span").xpath("text()").extract_first()
            item['author_link']=post.css('.fp_topic_poster').xpath("./a").xpath("@href").extract_first()
            item['condition']=condition
            #item['create_date']= post.css('.vt_first_timestamp').xpath('text()').extract().extend(response.css('.vt_reply_timestamp').xpath('text()').extract())
            #message = post.css('.vt_post_body').xpath('text()').extract()
            #item['post'] = self.cleanText(message)
            # item['post'] = re.sub('\s+',' '," ".join(post.css('.vt_post_body').xpath('text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
            item['tag']='breast-cancer'
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
