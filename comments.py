import requests
from pyquery import PyQuery as pq
import csv
import json
import jieba.analyse
import jieba
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import wordcloud
import re

short_comment = []
comment_ids = []
comment_content = []

data = {}

class DouBanComment(object):
    '''
        爬取评论：夏目友人帐
        保存格式：csv
        存入位置：comment.csv
    '''
    def __init__(self):
        self.url_login = 'https://accounts.douban.com/j/mobile/login/basic'
        self.session = requests.Session()
        self.name = '********'  # 这里换成自己的账号
        self.password = '********'  # 这里换成自己的密码

    def login(self):
        response = self.session.post(self.url_login, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:65.0) Gecko/20100101 Firefox/65.0',
                                                    'Accept':'application/json',
                                                 'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                                                 'X-Requested-With':'XMLHttpRequest',
                                                 'Cookie':'ll="118371"; bid=y4onL-Qp7h4; __utma=30149280.1043814831.1552288900.1552477604.1552641302.7; __utmz=30149280.1552641302.7.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _vwo_uuid_v2=D8E15CA56951750A5A9D3DE592973E7C8|17976caeba2695cf62cbe52214f6c23b; _pk_ref.100001.2fad=%5B%22%22%2C%22%22%2C1552641588%2C%22https%3A%2F%2Fmovie.douban.com%2Fsubject%2F27166442%2Fcomments%3Fstart%3D200%26limit%3D20%26sort%3Dnew_score%26status%3DP%22%5D; _pk_id.100001.2fad=4d314b9abb531886.1552302123.3.1552641655.1552305224.; push_noty_num=0; push_doumail_num=0; __utmv=30149280.17325; __utmb=30149280.3.10.1552641302; __utmc=30149280; __utmt=1; login_start_time=1552641657876; ap_v=0,6.0; _pk_ses.100001.2fad=*'},
                                 data = {'ck': '',
                                     'name': self.name,
                                     'remember': 'false',
                                     'password': self.password,
                                     'ticket': ''}
                             )

    # 获取热评
    def gethotComment(self):
        response = self.session.get(url = 'https://movie.douban.com/subject/27166442/comments?status=P',
                                headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:65.0) Gecko/20100101 Firefox/65.0'})
        doc = pq(response.text)
        comment_item = doc.find('.short')
        comment_id = doc.find('.comment-info')
        for id in comment_id.items():
            comment_ids.append(re.match('(.*?)\ ', id.text()).group(1))

        for item in comment_item.items():
            comment_content.append(item.text())


        page = 1
        while True:
            response = self.session.get(url='https://movie.douban.com/subject/27166442/comments?start='+ str(page*20) + '&limit=20&sort=new_score&status=P&comments_only=1',
                                    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:65.0) Gecko/20100101 Firefox/65.0'})
            info = json.loads(response.text)


            doc = pq(info['html'])
            if '还没有人写过短评' in doc.find('.comment-item').text():
                break;
            comment_item = doc.find('.short')
            comment_id = doc.find('.comment-info')
            for id in comment_id.items():
                comment_ids.append(re.match('(.*?)\ ', id.text()).group(1))

            for item in comment_item.items():
                comment_content.append(item.text())
            page = page + 1


        for i in range(len(comment_ids)):
            data[comment_ids[i]] = comment_content[i]
            short_comment.append(data)


    # 取得新评
    def getnewcomment(self):
        # 最新短评
        page = 0
        while True:
            if page == 0:
                response = self.session.get(
                    url='https://movie.douban.com/subject/27166442/comments?&sort=time&status=P&comments_only=1',
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:65.0) Gecko/20100101 Firefox/65.0'})
            else:
                response = self.session.get(url='https://movie.douban.com/subject/27166442/comments?start=' + str(
                    page * 20) + '&limit=20&sort=time&status=P&comments_only=1',
                                        headers={
                                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:65.0) Gecko/20100101 Firefox/65.0'})

            info = json.loads(response.text)
            doc = pq(info['html'])
            if '还没有人写过短评' in doc.find('.comment-item').text():
                break;
            comment_item = doc.find('.short')
            comment_id = doc.find('.comment-info')
            for id in comment_id.items():
                comment_ids.append(re.match('(.*?)\ ', id.text()).group(1))

            for item in comment_item.items():
                comment_content.append(item.text())
            page = page + 1

        for i in range(len(comment_ids)):
            data[comment_ids[i]] = comment_content[i]
            short_comment.append(data)


    # 写入csv文件
    def writer_to_csv(self):
        id_name = []
        content = []
        with open('comment.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                id_name.append(row[0])
                content.append(row[1])

        number = 0
        with open('comment.csv', 'a', errors='ignore', newline='') as f:
            writer = csv.writer(f)
            for k, w in short_comment[0].items():
                if k in id_name or w in content:
                    pass
                else:
                    print(k + ': ' + w)
                    writer.writerow([k.replace('\n', '').replace(' ', ''), w.replace('\n', '')])
                    number = number + 1
        print('共写入：'+str(number)+'条数据！')



    # 绘制云词图
    def makewordcloud(self):
        content = ''
        with open('comment.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                content += row[1]
                content = content + '\n'

        jieba.analyse.set_stop_words('stop.txt')
        tags = jieba.analyse.extract_tags(content, topK=100, withWeight=True)
        word_freq = {}
        for v, n in tags:
            word_freq[v] = str(int(n * 10000))
            word_freq[v] = int(n * 10000)

        mask = np.array(Image.open('index.png'))  # 定义词频背景
        wc = wordcloud.WordCloud(
            font_path='C:/Windows/Fonts/simhei.ttf',  # 设置字体格式
            mask=mask,  # 设置背景图
            max_words=2000,  # 最多显示词数
            max_font_size=120,  # 字体最大值
            background_color='white'
        )

        wc.generate_from_frequencies(word_freq)  # 从字典生成词云
        image_colors = wordcloud.ImageColorGenerator(mask)  # 从背景图建立颜色方案
        wc.recolor(color_func=image_colors)  # 将词云颜色设置为背景图方案
        plt.imshow(wc)  # 显示词云
        plt.axis('off')  # 关闭坐标轴
        plt.show()  # 显示图像'''


if __name__ == '__main__':
    douban = DouBanComment()
    douban.login()
    douban.getnewcomment()
    douban.gethotComment()
    douban.writer_to_csv()
    douban.makewordcloud()
