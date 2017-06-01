import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging, dateparser, time

class ForumsSpider(CrawlSpider):
    name = "hepc_medhelp_spider"
    allowed_domains = ["www.medhelp.org"]
    start_urls = [
        "http://www.medhelp.org/forums/Hepatitis-C/show/75",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="fonts_resizable_subject subject_title "]/a', 
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="msg_next_page"]'
                ), follow=True),
        )

    def getDate(self,date_str):
        # date_str="Fri Feb 12, 2010 1:54 pm"
        date = dateparser.parse(date_str)
        epoch = int(date.strftime('%s'))
        create_date = time.strftime("%Y-%m-%d'T'%H:%M%S%z",  time.gmtime(epoch))
        return create_date

    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//div[@id="new_posts_show_middle"]/div[@class="post_data has_bg_color"]')
        items = []
        condition = "hep c"
        topic = response.xpath('//div[@class="desc"]/text()').extract_first()
        url = response.url
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//div[@class="question_by"]/span/a/text()').extract_first()
            if item['author']:
                item['author_link'] = post.xpath('.//div[@class="question_by"]/span/a/@href').extract_first()

                create_date = self.getDate(self.cleanText(" ".join(post.xpath('.//div[@class="float_fix"]/div[2]/text()').extract()[1].strip())))
                item['create_date'] = create_date
          
                item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="KonaBody"]/text()').extract()).replace("\t","").replace("\n","").replace("\r","").replace(u'\xa0',''))
                item['tag']=''
                item['topic'] = topic.strip()
                item['url']=url
                logging.info(item.__str__)
                items.append(item)
        return items
