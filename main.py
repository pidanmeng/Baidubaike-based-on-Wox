# encoding=utf8
import requests
from bs4 import BeautifulSoup
import webbrowser
from wox import Wox, WoxAPI


# 用户写的Python类必须继承Wox类 https://github.com/qianlifeng/Wox/blob/master/PythonHome/wox.py
# 这里的Wox基类做了一些工作，简化了与Wox通信的步骤。
class Main(Wox):

    def request(self, url):
        return self.session.get(url)

    # 必须有一个query方法，用户执行查询的时候会自动调用query方法
    def query(self, key):
        results = []
        self.session = requests.session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (' \
                                             'KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36 '
        if not key:
            results.append({
                "Title": '请输入关键字',
                "SubTitle": '百度一下，你就知道',
                "IcoPath": "Images/app.ico"
            })
        else:
            url = 'https://baike.baidu.com/search/word?word=' + key
            res = self.request(url)
            res.encoding = 'utf-8'
            content_encoding = res.headers['Content-Encoding']
            soup = BeautifulSoup(res.text)
            if content_encoding == 'deflate':
                # headers中的Content Encoding的值为deflate，则证明query中的关键字直接匹配到百度百科的词条
                # 直接return结果即可
                description = soup.find_all(attrs={'name': 'description'})[0]['content']
                # description获取了页面下的概述字符串
                self.appendResult(results, key + '_百度百科', description, url)
            else:
                for i in soup.select(".search-list dd"):
                    title = i.contents[1].text
                    subtitle = i.contents[3].text
                    url = i.contents[1]['href']
                    self.appendResult(results, title, subtitle, url)
                if not len(results):
                    self.appendResult(results, '找不到结果', '未能找到' + key + '的相关信息，请重新输入', None)
        return results

    def openUrl(self, url):
        webbrowser.open(url)

    def appendResult(self, res, title, subtitle, url):
        """
        用于向result中添加项目
        :param res: 待添加的result列表
        :param title: 标题
        :param subtitle: 副标题
        :param url:指向的网页
        """
        res.append({
            "Title": title,
            "SubTitle": subtitle,
            "IcoPath": "Images/app.ico",
            "JsonRPCAction": {
                "method": "openUrl",
                "parameters": [url],
                "dontHideAfterAction": True
            }
        })


if __name__ == "__main__":
    Main()
