# weibo_comments_spider - 微博评论爬虫


## Requirements

Python 3.x  
[Scrapy 1.5.x](https://scrapy.org/)  
[Requests](https://2.python-requests.org/en/master/)  
[MongoDB](https://www.mongodb.com/)  
[pymongo](https://api.mongodb.com/python/current/)


## Feature

#### 目标网页

微博移动端网页（因为移动端容易爬）

#### 任务

微博热搜榜首页的每个话题，每个话题下的每条微博内容（严格来说不是并不是“每条”，只是前面很多条），每条微博内容下的第一批评论（移动端网页的评论每次只加载一部分，往下浏览的时候才会继续加载更多评论），第一批评论里的每一条评论，爬取这条评论的内容、评论者信息，如果这条评论底下有人回复，再爬取其中一条回复的内容、回复者信息。爬下来的数据用MongoDB储存。

#### 一些问题

**没有用上代理IP池：** 免费IP质量不高，效率还没有 “用自己的IP然后降低爬取频率” 那么高。

**只爬第一批评论：** 继续加载需要登录的Cookie，暂时没打算购买账号。

**用户信息有很多爬不下来：** 爬取用户信息比爬取微博内容更容易被反爬虫，频率限制更加严格，当被反爬虫时，在数据库先记录用户ID，以后再从数据库取出ID重新爬取补充数据。

## How to Use

In Python 3.x environment and the directory where `entry_point.py` exists, execute
```
python entry_point.py  # (run the spider once)
```
or 
```
nohup ./auto_run.sh &  # (run the spider every 2400 seconds)
```
