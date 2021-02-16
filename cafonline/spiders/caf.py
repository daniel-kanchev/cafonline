import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from cafonline.items import Article


class CafSpider(scrapy.Spider):
    name = 'caf'
    start_urls = ['https://www.cafonline.org/about-us/blog-home']

    def parse(self, response):
        articles = response.xpath('//div[@class="blogSummary"]')
        for article in articles:
            link = article.xpath('.//h3/a[@class="vs_link"]/@href').get()
            date = article.xpath('.//div[@class="sfitemDate"]//text()').get()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[text()="Next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1//text()').get()
        if title:
            title = title.strip()

        try:
            date = datetime.strptime(date.strip(), '%d %B %Y')
            date = date.strftime('%Y/%m/%d')
        except:
            date = 'No date'

        content = response.xpath('//div[@class="sf_colsOut sf_2cols_2_75 rightTextContent "]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[2:]).strip()

        author = response.xpath('//h3[@class="blog_grey"]/text()').get()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('author', author)

        return item.load_item()
