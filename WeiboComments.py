import requests
import datetime
from fake_useragent import UserAgent
import re
import os
import time

class WeiboCommentCrawler:

    def __init__(self,):
        # self.header = {
        #     "User-Agent": UserAgent().random,
        # }
        # self.cid = '107603{}'.format(user_id)

        # self.uid = user_id
        # self.since_id = ''

        # # 用户相关信息
        # self.username = ''

        # # 时间间隔信息
        # self.counter = time_counter
        pass
    # 将新浪微博时间转换作标准格式
    @staticmethod
    def __trans_time(v_str):
        # 转换GMT到标准格式
        GMT_FORMAT = '%a %b %d %H:%M:%S +0800 %Y'
        timeArray = datetime.datetime.strptime(v_str, GMT_FORMAT)
        ret_time = timeArray.strftime('%Y-%m-%d %H:%M:%S')
        return ret_time

    @classmethod
    def __get_name(cls, v_str):
        user_name = v_str['data']['cards'][1]['mblog']['user']['screen_name']
        return user_name

    @classmethod
    def __get_since_id(cls, v_str):
        items = v_str.get('data').get('cardlistInfo')
        print(items)
        # if items is not None:
        #     since_id = items['since_id']
        # else:
        #     # 设置末页结束条件
        #     since_id = '404'
        since_id='404'
        try:
            since_id=items['since_id']
        except:
            since_id = '404'
        return since_id

    # 获取since_id, username
    @classmethod
    def __get_info(self, session):
        
        li = []
        topic_url = 'https://m.weibo.cn/api/container/getIndex?uid={}&luicode=10000011&lfid={}&type=uid&value={}&containerid={}'.format(
            self.uid, self.cid, self.uid, self.cid)
        topic_url += '&since_id=' + str(self.since_id)
        # print(topic_url)
        #休眠2秒
        time.sleep(2)
        result = session.get(topic_url, headers=self.header, timeout=30)
        try:
            if result.status_code == 200:
                li.append(result.json())

                # 重新获取since_id，并改变值
                self.since_id = self.__get_since_id(result.json())
                # print(self.since_id)

                # 获取user_name
                if self.username == '':
                    self.username = self.__get_name(result.json())

                # print(self.username)
                # print(result.text)
        except session.ConnectionError as e:
            print('Error', e.args)
        return li
    @classmethod
    def __get_data(self, user_id,session,time_counter=9):
        #初始化变量
        self.header = {
            "User-Agent": UserAgent().random,
        }
        self.cid = '107603{}'.format(user_id)

        self.uid = user_id
        self.since_id = ''


        # 用户相关信息
        self.username = ''

        # 时间间隔信息，默认9个月
        self.counter = time_counter


        # 数据记录器
        li = []

        # 记录每个月的数据
        per_month = []

        # 记录月份时间序列
        month_id = []

        # timer system
        last_time = ''
        last_month = 0
        temp_month = 0  # 临时条件时间（因为微博是按时间顺序分配js的created_at）
        rest_month = 0  # 相隔月份数

        # 尝试事先声明的变量，减少重复回收和声明空间
        text = ''

        while rest_month <= self.counter and self.since_id != '404':
            page = self.__get_info(session)[0]['data']['cards']
            # print(page)
            for sentence in page:
                text = sentence['mblog']['text']
                timing = sentence['mblog']['created_at']

                dr = re.compile(r'<[^>]+>|转发微博|分享图片|\s|\n')
                text = dr.sub('', text)
                length = len(text)
                # print(length)

                # 确保文本长度小于50
                if 1 < length <= 50:
                    if last_time == '' and text != '':
                        last_time = self.__trans_time(timing)
                        # print(last_time)
                        last_month = int(last_time[5:7])

                        # 记录首个分片时间（截止时间）
                        month_id.append(last_time[:7])
                        # print(month_id)

                    if text != '':
                        # print(text)
                        temp_month = int(self.__trans_time(timing)[5:7])

                        if int(month_id[-1][5:]) != temp_month:
                            li.append(per_month)
                            month_id.append(self.__trans_time(timing)[:7])
                            # print(month_id)
                            per_month = []

                        # per_month.append([temp_month, text])
                        per_month.append([text])

            # 将时间月份差转换为约瑟夫问题
            if temp_month != 0:  # 防止同一月份导致
                rest_month = (last_month - temp_month + 12) % 12

        if len(per_month) != 0:
            li.append(per_month)

        return li[::-1], month_id  # 倒转使其按照先后顺序，之后截取真正在时间范围的数据

    @staticmethod
    def __save_file_user(filename, text,save_folder_path="用户爬取文本"):
        path = filename[:-8]
        # print(path)
        # folder = os.path.exists(f'{save_folder}/' + path)
        folder_path=f'{save_folder_path}/' + path
        os.makedirs(folder_path, exist_ok=True)
        # if not folder:
        #     os.mkdir(f'{save_folder}/' + path)
        with open('{}/{}.txt'.format(folder_path, filename), 'w', encoding='utf-8') as file:
            for row in text:
                line = ','.join(str(item) for item in row)
                file.write(line + '\n')
        print(filename + '数据已保存')

    #对外接口
    @classmethod
    def save_file_months(self,user_id, session,time_counter=9,save_folder_path="用户爬取文本"):
        text_data, month = self.__get_data(session=session,user_id=user_id,time_counter=time_counter)

        for j in range(len(month)):
            self.__save_file_user(self.username + '_' + month[j], text_data[j],save_folder_path=save_folder_path)


# if __name__ == '__main__':
#     uid = "2397417584"
#     Session = requests.session()
#     WeiboCrawler.save_file_months(uid=uid,session=Session,time_counter=9)
