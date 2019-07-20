import json
from scrapy import Spider, Request
from weibo_comments.items import WeiboCommentsItem


class WeiboCommentsRepliesSpider(Spider):
    name = "weibo_comments_replies_spider-v1"

    # download_delay = 1

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

    cookies_dict = {i.split('=')[0]:i.split('=')[1] for i in cookies_string.split('; ')}

    fake_headers = {
        "User-Agent": 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38'
                      '(KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        "X-XSRF-TOKEN": '5296b9'
    }

    start_url = \
        'https://m.weibo.cn/comments/hotflow?id=4394333224076108&' \
        'mid=4394333224076108&max_id_type=0'

    new_request_url = 'https://m.weibo.cn/comments/hotflow?id=4394333224076108&' \
                      'mid=4394333224076108&max_id={max_id}&max_id_type=0'


    def start_requests(self):
        yield Request(url=self.start_url,
                      headers=self.fake_headers,
                      cookies=self.cookies_dict,
                      callback=self.parse_item)

    def parse(self, response):
        pass

    def parse_item(self, response):
        # print(response)
        response_text = response.text
        results = json.loads(response_text)
        # print(results)
        if 'data' in results.keys():
            result = results['data']
            if 'data' in result.keys():
                for single_comment in result['data']:
                    # 项目的“comment”指的是评论，但新浪微博的代码中的“comments”指的是评论下面的回复
                    item = WeiboCommentsItem()
                    item['comment'] = single_comment.get('text')
                    if single_comment.get('comments'):
                        top1_reply = single_comment.get('comments')[0]
                        item['reply'] = top1_reply.get('text')
                    # print('------------\n',
                    #       item['comment'], '\n',
                    #       item['reply'] if 'reply' in item else 'no reply')
                    yield item
            max_id_in_result = result['max_id']
            yield Request(url=self.new_request_url.format(max_id=max_id_in_result),
                          headers=self.fake_headers,
                          cookies=self.cookies_dict,
                          callback=self.parse_item)
