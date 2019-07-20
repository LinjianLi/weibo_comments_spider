import json
import requests
from scrapy import Spider, Request
from weibo_comments_spider.items import WeiboCommentsSpiderItem


class WeiboCommentsRepliesSpider(Spider):
    """
    这一个版本的爬虫使用了 Python 的 Requests 库
    以处理爬取用户信息时出现 418 的情况
    但因为微博对于用户信息页面的反爬力度大很多
    所以爬到后面，每条数据的用户信息基本上都只保留了 ID，没能真的爬下来文字信息
    """
    name = "weibo_comments_replies_spider"
    download_delay = 2
    allowed_domains = ["m.weibo.cn"]
    fake_headers = {
        "User-Agent": 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38'
                      '(KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        "X-XSRF-TOKEN": '5296b9'
    }

    # 用户信息的 URL
    user_info_url = 'https://m.weibo.cn/api/container/getIndex?containerid=230283{user_id}' \
                    '_-_INFO&title=%E5%9F%BA%E6%9C%AC%E8%B5%84%E6%96%99' \
                    '&luicode=10000011&lfid=230283{user_id}'

    # 微博热搜榜的主页
    realtime_hot_url = 'https://m.weibo.cn/api/container/getIndex?containerid=106003type%3D25%26t%3D3%26disable_hot' \
                       '%3D1%26filter_type%3Drealtimehot&title=%E5%BE%AE%E5%8D%9A%E7%83%AD%E6%90%9C&extparam=pos' \
                       '%3D0_0%26mi_cid%3D100103%26cate%3D10103%26filter_type%3Drealtimehot%26c_type%3D30%26&luicode' \
                       '=10000011&lfid=231583 '
    # 对于某一个话题，需要不断获取该话题下的新内容，需要下面两个 URL
    single_topic_start_url = 'https://m.weibo.cn/api/container/getIndex?' \
                             '{container_information}&page_type=searchall'
    single_topic_new_request_url = 'https://m.weibo.cn/api/container/getIndex?' \
                                   '{container_information}&page_type=searchall&page={page} '
    # 对于某一条微博内容，需要不断获取该微博内容下的更多评论，需要下面两个 URL
    single_weibo_start_url = 'https://m.weibo.cn/comments/hotflow?' \
                             'id={id}&mid={mid}&max_id_type=0'

    # 因为获取更多评论需要登录、cookie，所以我现在只打算获取第一批评论，不构造新 Request 获取更多评论了，所以注释掉
    # single_weibo_new_request_url = 'https://m.weibo.cn/comments/hotflow?id={id}&' \
    #                                'mid={mid}&max_id={max_id}&max_id_type=0'

    # 被折叠的评论回复需要从这个 URL 获取
    folded_replies_url = 'https://m.weibo.cn/comments/hotFlowChild?cid={cid}&max_id=0&max_id_type=0'

    def start_requests(self):
        try:
            yield Request(url=self.realtime_hot_url,
                          headers=self.fake_headers,
                          callback=self.parse_realtime_hot)
        except:
            yield Request(url=self.realtime_hot_url,
                          headers=self.fake_headers,
                          callback=self.parse_realtime_hot)

    def parse(self, response):
        pass

    def parse_realtime_hot(self, response):
        """
        解析微博热搜榜首页的内容，从中抽取各个话题的信息，然后爬取内容
        """
        response_text = response.text
        results = json.loads(response_text)
        if results['ok'] == 0:
            raise Exception("In function [parse_realtime_hot], results['ok'] == 0")
        if 'data' in results.keys():
            result = results['data']
            if 'cards' in result.keys():
                cards = result['cards']
                realtime_hot_card = cards[0]  # cards里面有2个元素，第1个是实时热搜，第2个是实时上升
                if 'card_group' in realtime_hot_card.keys():
                    card_group = realtime_hot_card['card_group']
                    # card_group里面每个元素就是一个热搜词条
                    for card_group_elem in card_group:
                        topic = card_group_elem['desc']
                        scheme = card_group_elem['scheme']
                        topic_container_info = scheme.split('?')[1]
                        meta = {'topic': topic,
                                'topic_container_info': topic_container_info}
                        try:
                            yield Request(url=self.single_topic_start_url.
                                          format(container_information=topic_container_info),
                                          headers=self.fake_headers,
                                          callback=self.parse_topic,
                                          meta=meta)
                        except:
                            yield Request(url=self.single_topic_start_url.
                                          format(container_information=topic_container_info),
                                          headers=self.fake_headers,
                                          callback=self.parse_topic,
                                          meta=meta)

    def parse_topic(self, response):
        """
        爬取某一个话题下面的所有微博内容，只加载30次新内容，是“次”不是“条”
        并调用parse_item来爬取每条微博内容下面的第一批评论和回复
        """
        meta = response.meta
        topic = meta['topic']  # 运行时可能会报错，KeyError，但是其实是有这个Key的
        topic_container_info = meta['topic_container_info']
        response_text = response.text
        results = json.loads(response_text)
        if results['ok'] == 0:  # 如果是 0，我自己在浏览器打开，显示“这里还没有内容”，应该表示这个话题爬完了
            return
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
                                meta = {'topic': topic,
                                        'topic_container_info': topic_container_info,
                                        'content': content,
                                        'mblog_id': mblog_id}
                                try:
                                    yield Request(url=self.single_weibo_start_url.
                                                  format(id=mblog_id, mid=mblog_id),
                                                  # cookies=self.cookies_dict,
                                                  headers=self.fake_headers,
                                                  callback=self.parse_item,
                                                  meta=meta)
                                except:
                                    yield Request(url=self.single_weibo_start_url.
                                                  format(id=mblog_id, mid=mblog_id),
                                                  # cookies=self.cookies_dict,
                                                  headers=self.fake_headers,
                                                  callback=self.parse_item,
                                                  meta=meta)
        # 处理完一批微博内容及对应评论之后，获取下一批微博内容
        # 总共只加载30次新内容，是“次”不是“条”，
        # 因此page到了30就不再继续爬这个话题
        if 'this_page' in response.meta:
            next_page = response.meta['this_page'] + 1
        else:
            next_page = 2
        if next_page == 31:
            return  # 加载了30次新内容后就return
        try:
            yield Request(url=self.single_topic_new_request_url.
                          format(container_information=topic_container_info,
                                 page=next_page),
                          headers=self.fake_headers,
                          callback=self.parse_topic,
                          meta={'this_page': next_page})
        except:
            yield Request(url=self.single_topic_new_request_url.
                          format(container_information=topic_container_info,
                                 page=next_page),
                          headers=self.fake_headers,
                          callback=self.parse_topic,
                          meta={'this_page': next_page})

    def parse_item(self, response):
        """
        爬取这条微博下面的第一批评论及回复
        """
        meta = response.meta
        topic = meta['topic']
        mblog_id = meta['mblog_id']
        content = meta['content'] if 'content' in meta else 'no content'
        results = json.loads(response.text)
        if results['ok'] == 0:  # 如果是 0，应该是这条微博下面根本就没有评论
            # raise Exception("results['ok'] == 0")
            return
        if 'data' in results.keys():
            result = results['data']
            if 'data' in result.keys():
                for single_comment in result['data']:
                    # 项目的“comment”指的是评论，但新浪微博的代码中的“comments”指的是评论下面的回复
                    item = WeiboCommentsSpiderItem()
                    item['topic'] = topic
                    item['content'] = content
                    item['comment'] = single_comment.get('text')
                    if single_comment['more_info_type'] == 1:
                        top1_reply = single_comment.get('comments')[0]
                        item['reply'] = top1_reply.get('text')
                        replier_id = top1_reply['user']['id']
                    elif single_comment['more_info_type'] == 2:
                        s_c_id = single_comment['id']
                        replies = requests.get(url=self.folded_replies_url.format(cid=s_c_id),
                                               headers=self.fake_headers,
                                               timeout=2).text
                        replies = json.loads(replies)
                        top1_reply = replies['data'][0]
                        item['reply'] = top1_reply.get('text')
                        replier_id = top1_reply['user']['id']
                    else:
                        replier_id = ''
                    commenter_id = single_comment['user']['id']
                    item['commenter'] = self.parse_user_info(commenter_id)
                    if replier_id != '':
                        item['replier'] = self.parse_user_info(replier_id)
                    yield item
            # 处理完一条微博底下的一批评论后，获取该条微博下一批评论
            # 因为这个功能需要登录，要cookie，我没有那么多账号，所以我注释掉了这部分代码
            # max_id_in_result = result['max_id']
            # yield Request(url=self.single_weibo_new_request_url.
            #               format(id=mblog_id, mid=mblog_id, max_id=max_id_in_result),
            #               headers=self.fake_headers,
            #               cookies=self.cookies_dict,
            #               callback=self.parse_item,
            #               meta=meta)

    def parse_user_info(self, user_id):
        user_info = ''
        user_info_req = requests.get(self.user_info_url.format(user_id=user_id),
                                     headers=self.fake_headers,
                                     timeout=2)
        if user_info_req.status_code != 200:
            user_info = '<user_id: ' + str(user_id) + '; ' + 'user_info: anti-crawled>'
        else:
            user_info_json = user_info_req.text
            user_info_json = json.loads(user_info_json)
            if user_info_json['ok'] == 0:
                raise Exception("In function [parse_user_info],  user_info['ok'] == 0")
            if 'data' in user_info_json.keys():
                result = user_info_json['data']
                account_info = result['cards'][0]['card_group']  # 账号信息
                person_info = result['cards'][1]['card_group']  # 个人信息
                for acc_info_elem in account_info:
                    user_info += (acc_info_elem['item_name'] + ':') if 'item_name' in acc_info_elem else ''
                    user_info += (acc_info_elem['item_content'] + '; ') if 'item_content' in acc_info_elem else ''
                for person_info_elem in person_info:
                    user_info += (person_info_elem['item_name'] + ':') if 'item_name' in person_info_elem else ''
                    user_info += (person_info_elem['item_content'] + '; ') if 'item_content' in person_info_elem else ''
        return user_info
