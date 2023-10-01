import os.path
import time
import requests
from retrying import retry
from fake_useragent import UserAgent
import re
import datetime
from HaoChiUtils import DataPreprocess

class WeiboCommentCrawler:
    DP=DataPreprocess()
    def __init__(self, user_id, timer, stopwords_file_path="hit_stopwords.txt"):
        self.headers = {
            "User-Agent": UserAgent().random,
        }

        self.timer = timer

        self.cid = cid = '107603{}'.format(user_id)
        self.uid = user_id
        self.since_id = ''

        self.user_name = ''
        self.counter = timer

        # 指定的停用词
        self.__stop_terms = ["展开", "全文", "显示原图", "显示地图",'转发微博','分享图片']

        # 停用词表
        self.__stopwords = []

        # 加载停用词列表

        with open(stopwords_file_path, "r", encoding="utf-8") as stopwords_file:
            for line in stopwords_file:
                self.__stopwords.append(line.strip())

   

    # 将新浪微博时间转换作标准格式
    @staticmethod
    def trans_time(v_str):
        # 转换GMT到标准格式
        GMT_FORMAT = '%a %b %d %H:%M:%S +0800 %Y'
        timeArray = datetime.datetime.strptime(v_str, GMT_FORMAT)
        ret_time = timeArray.strftime('%Y-%m-%d %H:%M:%S')
        return ret_time

    @classmethod
    def get_items(cls, v_str):
        items = v_str.get('data').get('cardlistInfo')
        return items

    # 使用retry修饰函数，进行重传机制
    @retry(stop_max_attempt_number=10, wait_random_min=2000, wait_random_max=2500)
    def _get_request(self, session):
        topic_url = 'https://m.weibo.cn/api/container/getIndex?uid={}&luicode=10000011&lfid={}&type=uid&value={}&containerid={}'.format(
            self.uid, self.cid, self.uid, self.cid)
        topic_url += '&since_id=' + str(self.since_id)
        # print(topic_url)
        response = session.get(topic_url, headers=self.headers)
        try:
            text = response.json()
        except:
            raise Exception('Connection error!')

        items = self.get_items(text)
        if items is None:
            raise Exception("Item back!")

        self.since_id = items['since_id']
        # print('{}\t'.format(self.since_id))

        if self.user_name == '':
            self.user_name = text['data']['cards'][0]['mblog']['user']['screen_name']
        return text

    def save_file(self, data, begin):
        folder_path=rf"爬取文本/{self.user_name}"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        filename = self.user_name + '_' + begin
        with open('{}/{}.txt'.format(folder_path, filename), 'w', encoding='utf-8') as op:
            for row in data:
                line = ','.join(str(item) for item in row)
                op.write(line + '\n')
            op.close()
        print(filename + '数据已保存')
        return folder_path


    def get_data(self, session):
        # 数据记录器
        li = []

        # 消除链接的正则表达式
        dr = re.compile(r'<[^>]+>|\s|\n')

        # 设置临时存储年-月的变量，设置月份记录
        last_month = ''
        current_month = ''
        folder_path=""
        while self.timer > 0:
            try:
                page = self._get_request(session)['data']['cards']
            except:
                return folder_path
            for sentence in page:
                text = dr.sub('', sentence['mblog']['text'])
                text = self.DP.text_clean(text)
                if len(text) < 3:
                    text = ''
                if text != '':
                    current_month = self.trans_time(sentence['mblog']['created_at'])[:7]
                    if len(last_month) == 0 or last_month != current_month:
                        # 检测是否满足结果要求
                        if self.timer == 0:
                            break
                        # 进行文件保存操作
                        if len(li) >= 5:
                            # print('1')
                            folder_path=self.save_file(li, last_month)
                            self.timer -= 1
                        li.clear()
                        last_month = current_month
                        print('正在查询时间为{}的记录'.format(last_month))
                    li.append([text])
        # print(li)
        return folder_path


import concurrent.futures


def multi_crawler(user_ids, time_counter):
    spiders = [WeiboCommentCrawler(user_ids[i], time_counter) for i in range(len(user_ids))]
    params = [(requests.session()) for _ in range(len(user_ids))]

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(spi.get_data, param) for spi, (param) in
                   zip(spiders, params)]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print("Exception multiprocess:", e)


def read_txt(path):
    with open(path, 'r', encoding='utf-8') as txt:
        lines = txt.read().split('\n')[1:-1]
        # print(lines)
        return lines


if __name__ == '__main__':

    uid = input("uid:")

    # uid = "123"
    count = 9
    spider = WeiboCommentCrawler(uid, count)
    session = requests.session()
    spider.get_data(session)
    # res=DP.text_clean("转发微博")
    # print("res=",res)
