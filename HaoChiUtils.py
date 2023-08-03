# 导入所需的库
import re
import csv
import jieba
import emoji
from opencc import OpenCC
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt


#================================================by Chi================================================
#定义数据预处理类 
#包含 清洗文本、将清洗后的文本存入文件方法
class DataPreprocess:

    # 指定的停用词
    __stop_terms = ["展开", "全文", "转发", "显示原图", "原图","显示地图",'转发微博','分享图片']

    #停用词表
    __stopwords = []

    def __init__(self,stopwords_file_path = "hit_stopwords.txt") :
        # 加载停用词列表
        
        with open(stopwords_file_path, "r", encoding="utf-8") as stopwords_file:
            for line in stopwords_file:
                self.__stopwords.append(line.strip())

    
    # 定义清洗文本的函数
    @classmethod
    def text_clean(self,text,has_user_id=False, keep_segmentation=False):
    #当keep_segmentation为False时，text_clean方法会使用jieba库对清洗后的文本进行分词处理，并返回分词后的结果。       

        # 使用OpenCC库将繁体中文转换为简体中文
        cc = OpenCC('t2s')
        text = cc.convert(text)

        #如果有用户id
        if has_user_id:
            # 去除冒号后的内容
            for i in range(len(text)):
                if text[i] == ':' or text[i] == '：':
                    text = text[i + 1:-1]
                    break

        # 定义中文标点符号和URL正则表达式
        zh_puncts1 = "，；、。！？（）《》【】\"\'"
        URL_REGEX = re.compile(
            r'(?i)((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>' +
            zh_puncts1 + ']+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|'
            r'[^\s`!()\[\]{};:\'".,<>?«»“”‘’' + zh_puncts1 + ']))',re.IGNORECASE)
        
        # 去除URL
        text = re.sub(URL_REGEX, "", text)
        


        # 去除@用户和回复标记
        text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:|：| |$)", " ", text)
        
        # 去除表情符号
        text = re.sub(r"\[\S+?\]", "", text)

        #去除中文标点
        # 使用re.sub()函数将标点符号替换为空格
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # 去除话题标签
        text = re.sub(r"#\S+#", "", text)
        
        # 去除多余的空格
        text = re.sub(r"(\s)+", r"\1", text)
        
        # 去除数字
        text = re.sub(r'\d+', '', text)

        for x in self.__stop_terms:
            text = text.replace(x, "")
        
        # 去除首尾空格
        text = text.strip()
        
        # 将表情符号转换为文本描述
        text = emoji.demojize(text)
        if keep_segmentation:
            return text
        else:
            # 使用结巴分词进行分词
            seg_list = list(jieba.cut(text,cut_all=False))        
            # 去除停用词
            seg_list = [word for word in seg_list if word not in self.__stopwords]
            # 将分词结果拼接为字符串
            cleaned_text = ' '.join(seg_list)
        
        return cleaned_text


    #只能处理文件格式为 text label且以\t为分隔符 的文件
    @classmethod
    def text_process(self,input_file_path="DataSet.tsv", output_file_path="Clean_data.tsv"):

        count=1
        # 打开输入文件并读取内容
        with open(input_file_path, "r", encoding="utf-8") as input_file:
            lines = input_file.readlines()
            cleaned_lines = []
            
            # 遍历每一行数据
            for line in lines:
                
                line = line.strip().split('\t')
                if line[1]=="label":
                    print(line[1])
                    continue
                if count%500==0:
                    print(f"已处理{count}条文本记录")
                count+=1

                # 检查列表长度是否足够
                if len(line) == 2:
                    # 调用clean_text函数清洗第一列的文本数据，并保留其他几列数据
                    clean_text=self.text_clean(line[0])
                    # 删去第一列内容为空的行
                    if clean_text !='':
                        cleaned_line = [self.text_clean(line[0]),line[1]]

                    cleaned_lines.append(cleaned_line)
            
            
            
            # 打开输出文件并写入清洗后的数据，写入csv
            with open(output_file_path, "w", encoding="utf-8", newline='') as output_file:
                writer = csv.writer(output_file,delimiter='\t')
                for line in cleaned_lines:
                    writer.writerow(line)
            print(f"共有{len(cleaned_lines)}条记录！")
            # # 输出提示信息
            # print("修改后的内容已写入新文件。")


# ================================by Hao=====================================
#数据分析类
#包含 划分数据集、绘制训练曲线、计算标签占比方法
class DataAnalyzer:

    def __init__(self) -> None:
        pass


    #划分数据集为测试集、验证集、训练集
    @classmethod
    def split_dataSet(self,dataSet_path='dataSet.tsv'):
        # 读取数据集
        data = pd.read_csv(dataSet_path, delimiter='\t')

        # 划分训练集和剩余数据
        train_data, remaining_data = train_test_split(data, test_size=0.2, random_state=42)

        # 划分验证集和测试集
        valid_data, test_data = train_test_split(remaining_data, test_size=0.5, random_state=42)

        # 保存划分后的数据集
        train_data.to_csv('train.tsv', sep='\t', index=False)
        valid_data.to_csv('eval.tsv', sep='\t', index=False)
        test_data.to_csv('test.tsv', sep='\t', index=False)

    # 绘制训练过程的曲线
    @classmethod
    def draw_process(self, title='trainning acc', color='r', iters=[], data=[], label='trainning acc', png_path='plot'):
        # 设置图表标题和字体大小
        plt.title(title, fontsize=24)
        # 设置x轴标签和字体大小
        plt.xlabel("iter", fontsize=20)
        # 设置y轴标签和字体大小
        plt.ylabel(label, fontsize=20)
        # 绘制曲线，使用指定的颜色和标签
        plt.plot(iters, data, color=color, label=label)
        # 添加图例
        plt.legend()
        # 添加网格线
        plt.grid()
        # 保存图表为PNG格式图片
        plt.savefig(png_path+'/'+label+'.png')
        # 显示图表（可选）
        # plt.show()


    # 计算标签占比，输入为预测结果的列表，输出为标签:占比(0.xx)
    @classmethod
    def calculate_label_proportions(self,predictions,label_list):
        # 创建一个空字典用于存储标签及其对应的数量
        predictions_dict = {}
        #添加字典
        for i in label_list:
            predictions_dict[i]=0
        # 初始化总数量为0
        total_cnt = 0
        # 遍历预测结果列表
        for prediction in predictions:
            # 如果标签不在字典的键中，则将其添加到字典并初始化数量为0
            if prediction not in predictions_dict.keys():
                predictions_dict[prediction] = 0
            # 将标签对应的数量加1
            predictions_dict[prediction] += 1
            # 总数量加1
            total_cnt += 1
        # # 创建一个空字典用于存储标签及其对应的占比
        res_dict = {}
        # 遍历标签及其对应的数量
        for key, value in predictions_dict.items():
            # # 为每个标签创建一个子字典
            # res_dict[key] = {}
            # # 将标签的总数量存储到子字典中
            # res_dict[key]['total'] = value
            # # 计算标签的占比，并保留一位小数
            proportion = round(value / total_cnt , 2)
            # 将占比存储到子字典中
            res_dict[key] = proportion
        # 返回标签及其对应的占比字典
        return res_dict
    

    #转化为列表可供模型读取
    #data_file_path:    文件路径
    #min_len:           文本的最小长度
    @classmethod
    def get_dataList(self,data_file_path,min_len=0):
        ret_list=[]
        with open(data_file_path,'r',encoding='utf-8') as f:
            for data_line in f:
                data_line=data_line.strip().strip('\n')
                ##文本清洗：删除@或url等无关信息
                #需要嵌入代码
                data_line=DataPreprocess.text_clean(text=data_line,has_user_id=False,keep_segmentation=True)

                if data_line is not None and len(data_line) >=min_len:
                    ret_list.append(data_line)
        return ret_list
