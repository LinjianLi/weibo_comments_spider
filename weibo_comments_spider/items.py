# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboCommentsSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    topic = scrapy.Field()      # 微博话题
    content = scrapy.Field()    # 该话题下本条微博内容
    comment = scrapy.Field()    # 本条微博的一个评论
    commenter = scrapy.Field()  # 本评论的作者
    reply = scrapy.Field()      # 本评论的一个回复
    replier = scrapy.Field()    # 本回复的作者
