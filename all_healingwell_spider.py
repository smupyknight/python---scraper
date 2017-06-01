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

# # LOGGING to file
# import logging
# from scrapy.log import ScrapyFileLogObserver

# logfile = open('testlog.log', 'w')
# log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
# log_observer.start()

# Spider for crawling Adidas website for shoes

# epilepsy, etc
class ForumsSpider(CrawlSpider):
    name = "all_healingwell_spider"
    allowed_domains = ["www.healingwell.com"]
    start_urls = [
        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//tr/td[contains(@class,"TopicTitle")]/a',
                canonicalize=True,
                ), callback='parsePost'),
            # Rule to follow arrow to next product grid
            # Rule(LinkExtractor(
            #    restrict_xpaths="//tr[td[contains(., 'forums')]][last()]/td[contains(., 'forums')]/br/a",
            # ), follow=True),
            Rule(LinkExtractor(
                restrict_xpaths='//a',
                canonicalize=True,
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
    def parsePost(self, response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.css("Table.PostBox")
        breadcrumbs = sel.css("#Breadcrumbs")
        # condition = breadcrumbs.xpath("./a[3]/text()")
        condition = breadcrumbs.xpath("./a[3]/text()").extract()[0]
        items = []
        topic = response.xpath('//div[contains(@id,"PageTitle")]/h1/text()').extract()[0]
        url = response.url
        for post in posts:
            item = PostItemsList()
            item['author'] = post.css('.msgUser').xpath("./a[2]").xpath("text()").extract()[0]
            item['author_link'] = post.css('.msgUser').xpath("./a[2]/@href").extract()[0]
            item['condition'] = condition

            create_date = self.getDate(self.cleanText(" ".join(re.sub(" +|\n|\r|\t|\0|\x0b|\xa0", ' ', response.css('td.msgThreadInfo').xpath('text()').extract()[0]).strip())))
            item['create_date'] = create_date

            post_msg = self.cleanText(post.css('.PostMessageBody').extract()[0])
            item['post'] = post_msg
            item['tag'] = ''
            item['topic'] = topic
            item['url'] = url
	    logging.info(post_msg)
            items.append(item)
        return items
