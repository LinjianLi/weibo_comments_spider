# !/usr/bin/env python

import scrapy
from scrapy.cmdline import execute

execute(['scrapy', 'crawl', 'weibo_comments_replies_spider'])

# execute(['scrapy', 'crawl', 'check_header_spider'])

