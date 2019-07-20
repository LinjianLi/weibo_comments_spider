import json
from scrapy import Spider, Request
from weibo_comments_spider.items import WeiboCommentsSpiderItem


class WeiboCommentsRepliesSpider(Spider):
    name = "weibo_comments_replies_spider-v2"

    # download_delay = 0.5

    allowed_domains = ["m.weibo.cn"]

    cookies_string = "_T_WM=36297874767; WEIBOCN_FROM=1110003030; " \
                     "SUB=_2A25wKZWKDeRhGeRH7loY9C7IzTyIHXVT1TvCrDV6PUJbkdBeLXXTkW1NTdrQPhqFVluLsS3SPoHSm3XuBvHdb55z; " \
                     "SUHB=05iqmhbBw9VmLc; " \
                     "SCF=AiW4O_9XJ5JAq7LNkGXRZXtTGvKIDThU714CzrezKDbVoTEVj6rYGuBz8rBibYc3iDzd6UKv-CHha2mwthoA6m4.; " \
                     "SSOLoginState=1563289050; MLOGIN=1; XSRF-TOKEN=5296b9; " \
                     "M_WEIBOCN_PARAMS=oid%3D4394333224076108%26luicode%3D10000011%26lfid%3D231522type%253D1%2526t" \
                     "%253D10%2526q%253D%2523%25E6%259D%25AD%25E5%25B7%259E%25E5%25A5%2594%25E9%25A9%25B0%25E5%25A4" \
                     "%25B1%25E6%258E%25A7%25E6%2592%259E%25E4%25BA%25BA%25E6%25A1%2588%25E5%25AE%25A3%25E5%2588%25A4" \
                     "%2523%26uicode%3D20000061%26fid%3D4394333224076108 "

    cookies_dict = {i.split('=')[0]: i.split('=')[1] for i in cookies_string.split('; ')}

    fake_headers = {
        "User-Agent": 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38'
                      '(KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        "X-XSRF-TOKEN": '5296b9'
    }

    start_url = \
        'https://m.weibo.cn/api/container/getIndex?containerid=231522type%3D1%26t%3D10%26q%3D%23%E6%9D%AD%E5%B7%9E%E5' \
        '%A5%94%E9%A9%B0%E5%A4%B1%E6%8E%A7%E6%92%9E%E4%BA%BA%E6%A1%88%E5%AE%A3%E5%88%A4%23&extparam=%23%E6%9D%AD%E5' \
        '%B7%9E%E5%A5%94%E9%A9%B0%E5%A4%B1%E6%8E%A7%E6%92%9E%E4%BA%BA%E6%A1%88%E5%AE%A3%E5%88%A4%23&luicode=20000061' \
        '&lfid=4394333224076108&page_type=searchall '

    new_request_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231522type%3D1%26t%3D10%26q%3D%23%E6%9D' \
                      '%AD%E5%B7%9E%E5%A5%94%E9%A9%B0%E5%A4%B1%E6%8E%A7%E6%92%9E%E4%BA%BA%E6%A1%88%E5%AE%A3%E5%88%A4' \
                      '%23&extparam=%23%E6%9D%AD%E5%B7%9E%E5%A5%94%E9%A9%B0%E5%A4%B1%E6%8E%A7%E6%92%9E%E4%BA%BA%E6%A1' \
                      '%88%E5%AE%A3%E5%88%A4%23&luicode=20000061&lfid=4394333224076108&page_type=searchall&page={page} '

    single_weibo_start_url = \
        'https://m.weibo.cn/comments/hotflow?id={id}&' \
        'mid={mid}&max_id_type=0'

    single_weibo_new_request_url = 'https://m.weibo.cn/comments/hotflow?id={id}&' \
                                   'mid={mid}&max_id={max_id}&max_id_type=0'

    def start_requests(self):
        try:
            yield Request(url=self.start_url,
                          headers=self.fake_headers,
                          callback=self.parse_topic)
        except:
            yield Request(url=self.start_url,
                          headers=self.fake_headers,
                          callback=self.parse_topic)

    def parse(self, response):
        pass

    def parse_topic(self, response):
        """
        爬取某一个话题下面的所有微博内容
        并调用parse_item来爬取每条微博内容下面的所有评论和回复
        """
        response_text = response.text
        results = json.loads(response_text)
        # print(response)
        if 'data' in results.keys():
            result = results['data']
            if 'cards' in result.keys():
                cards = result['cards']
                for card in cards:
                    if 'card_group' in card.keys():
                        card_group = card['card_group']
                        # card_group里面每个元素就是一条微博或者是一个其他类型的card
                        for card_group_elem in card_group:
                            if 'mblog' in card_group_elem:
                                mblog = card_group_elem['mblog']
                                if 'text' in mblog:
                                    content = mblog['text']
                                if 'id' in mblog:
                                    mblog_id = mblog['id']
                                meta = {'content': content,
                                        'mblog_id': mblog_id}
                                try:
                                    yield Request(url=self.single_weibo_start_url.
                                                  format(id=mblog_id, mid=mblog_id),
                                                  cookies=self.cookies_dict,
                                                  headers=self.fake_headers,
                                                  callback=self.parse_item,
                                                  meta=meta)
                                except:
                                    yield Request(url=self.single_weibo_start_url.
                                                  format(id=mblog_id, mid=mblog_id),
                                                  cookies=self.cookies_dict,
                                                  headers=self.fake_headers,
                                                  callback=self.parse_item,
                                                  meta=meta)
        if 'this_page' in response.meta:
            next_page = response.meta['this_page'] + 1
        else:
            next_page = 2
        # 处理完一批微博内容及对应评论之后，获取下一批微博内容
        try:
            yield Request(url=self.new_request_url.
                          format(page=next_page),
                          headers=self.fake_headers,
                          callback=self.parse_topic,
                          meta={'this_page': next_page})
        except:
            yield Request(url=self.new_request_url.
                          format(page=next_page),
                          headers=self.fake_headers,
                          callback=self.parse_topic,
                          meta={'this_page': next_page})

    def parse_item(self, response):
        """
        爬取这条微博下面的第一批评论及回复
        """
        meta = response.meta
        mblog_id = meta['mblog_id']
        content = meta['content'] if 'content' in meta else 'no content'
        results = json.loads(response.text)
        if results['ok'] == 0:
            raise Exception("results['ok'] == 0")
        if 'data' in results.keys():
            result = results['data']
            if 'data' in result.keys():
                for single_comment in result['data']:
                    # 项目的“comment”指的是评论，但新浪微博的代码中的“comments”指的是评论下面的回复
                    item = WeiboCommentsSpiderItem()
                    item['content'] = content
                    item['comment'] = single_comment.get('text')
                    if single_comment.get('comments'):
                        top1_reply = single_comment.get('comments')[0]
                        item['reply'] = top1_reply.get('text')
                    yield item
            # max_id_in_result = result['max_id']
            # 处理完一条微博底下的一批评论后，获取该条微博下一批评论
            # yield Request(url=self.single_weibo_new_request_url.
            #               format(id=mblog_id, mid=mblog_id, max_id=max_id_in_result),
            #               headers=self.fake_headers,
            #               cookies=self.cookies_dict,
            #               callback=self.parse_item,
            #               meta=meta)
