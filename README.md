# weibo_comments_spider


## Requirements

Python 3.x  
[Scrapy](https://scrapy.org/)  
[Requests](https://2.python-requests.org/en/master/)  
[MongoDB](https://www.mongodb.com/)  
[pymongo](https://api.mongodb.com/python/current/)


## Feature

#### 目标网页

微博移动端网页

#### 任务

微博热搜榜首页的每个话题，每个话题下的每条微博内容（严格来说不是并不是“每条”，只是前面很多条），每条微博内容下的第一批评论（移动端网页的评论每次只加载一部分，往下浏览的时候才会继续加载更多评论），第一批评论里的每一条评论，爬取这条评论的内容、评论者信息，如果这条评论底下有人回复，再爬取其中一条回复的内容、回复者信息。爬下来的数据用MongoDB储存。
