#项目主模块
from HaoChiUtils import DataAnalyzer as DA
from MyModel import Classification
import math
import os
import matplotlib.pyplot as plt                #导入绘图包
from matplotlib import font_manager as fm
from matplotlib import cm
import numpy as np
plt.rcParams['font.sans-serif'] = ['SimHei']   #解决中文显示问题
plt.rcParams['axes.unicode_minus'] = False    # 解决中文显示问题

#Depression risk inference
class DRI:
    #结果1的阈值
    # __result1_threshold= 58.32
    __result1_threshold= 44.82

    # 熵率的阈值
    # __entropy_threshold=0.0762
    __entropy_threshold=0.0872

    #悲伤情绪占比阈值
    __sadness_proportion_threshold=0.65
    #情绪变化阈值
    __mood_change_threshold=0.35

    #指标
    __score1=__result1_threshold
    __score2=__score1+(130*0.7-__score1)/3
    __score3=__score2+(130*0.7-__score2)/3

    
    #情绪标签
    label_list=['快乐','恐惧','愤怒','惊讶','喜爱','厌恶','悲伤']

    
    def __init__(self,model_path="bert_model"):
        #加载模型
        self.myClassification=Classification(model_path)

    #计算结果1
    #传入标签占比，保留2位小数
    def get_result1(self, pro_dict):
        # 定义权重列表
        weight_list = [-1, 0.5, 1, 0, -1.5, 0.5, 1.3]
        # 初始化结果
        result = 0
        # 遍历标签列表
        for i in range(len(self.label_list)):
            # 计算结果
            result += pro_dict[self.label_list[i]] * weight_list[i] * 100
        # 返回结果并保留两位小数
        return round(result, 2)
    

    #计算熵率
    #传入标签占比,保留5位小数
    def get_entropy(self, pro_dict, time_interval=20):
        # 初始化总概率
        total_pi = 0
        # 遍历标签列表
        for i in range(len(self.label_list)):
            # 获取标签对应的概率
            pi = pro_dict[self.label_list[i]]
            # 如果概率大于0
            if pi > 0:
                # 计算熵
                total_pi += -pi * math.log2(pi)
        # 返回平均熵并保留五位小数
        return round(total_pi / time_interval, 5)

    #得到占比标签
    #data 为待预测的数据
    def get_pro_dict(self, data):
        # 获取预测结果列表
        pre_list = self.myClassification.get_predict_result(data)
        # 计算标签比例字典
        pro_dict = DA.calculate_label_proportions(pre_list, label_list=self.label_list)
        # 返回标签比例字典
        return pro_dict
    
    # 得到情绪稳态
    # 情绪稳态：找占比最低的情绪，看有没有大于它20%以上的情绪存在，
    # 有，情绪稳态=True，无，情绪稳态=False
    def get_emotional_homeostasis(self, pro_dict, threshold=0.2):
        # 初始化最小占比和最大占比
        min_proportion = 1
        max_proportion = 0
        # 遍历标签列表
        for i in self.label_list:
            # 如果占比小于最小占比且不是'惊讶'标签且占比大于0
            if pro_dict[i] < min_proportion and i != '惊讶' and pro_dict[i] > 0:
                # 更新最小占比
                min_proportion = pro_dict[i]
            # 如果占比大于最大占比且不是'惊讶'标签且占比大于0
            if pro_dict[i] > max_proportion and i != '惊讶' and pro_dict[i] > 0:
                # 更新最大占比
                max_proportion = pro_dict[i]
        # 如果最大占比与最小占比之差大于阈值
        if max_proportion - min_proportion > threshold:
            return True
        # 情绪稳态False
        return False


    #风险评估
    def risk_assessment(self,user_path="",min_len=1,min_text_num=5):


        #待预测文本列表
        data_list=DA.get_dataList(user_path,min_len=min_len)

        #情绪占比
        pro_dict=self.get_pro_dict(data_list)
        #熵率
        entropy=self.get_entropy(pro_dict)
        #结果1
        result1=self.get_result1(pro_dict)
        #稳态
        emotional_homeostasis=self.get_emotional_homeostasis(pro_dict)
        #标准差
        S=self.get_standard_deviation(pro_dict=pro_dict)

        if pro_dict['悲伤']<=self.__sadness_proportion_threshold:
            if S<self.__mood_change_threshold:
                result1*=0.9
            else:
                result1*=1.1

        score=0
        # print("result1=",result1)
        #风险评估
        if result1 < self.__result1_threshold or len(data_list)<min_text_num:
            # print("小于result1阈值，分数=",result1)
            return 0
        
        elif emotional_homeostasis==True and entropy>=self.__entropy_threshold:
            score=result1*1.2

        elif emotional_homeostasis==False and entropy<self.__entropy_threshold:
            score=result1*0.8
            
        else:
            score=result1

        # 判断风险等级
        risk_level=self.judge_rank(score)

        return risk_level

    #分数转化为风险等级
    def judge_rank(self,score):
        
        if score>self.__score1 and score<self.__score2:
            return 1
        elif score>=self.__score2 and score<self.__score3: 
            return 2
        elif score>=self.__score3:
            return 3
        return 0
    
    #画饼状图
    def draw_pie(self,pro_dict,dest_path):
        labels = list(pro_dict.keys())
        probs = list(pro_dict.values())

        # 自定义颜色列表
      
        colors = ['#FF6347', '#FFD700', '#FFFF00', '#32CD32', '#B0E0E6', '#6495ED', '#9932CC']
        # colors = cm.GnBu(np.arange(len(labels),0,-2) / len(labels))
        # 自定义偏移量列表
        explode = (0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1)
        plt.figure(figsize=(10, 8),facecolor='lightgray')
        # 设置标签字体属性
        plt.pie(probs, labels=labels,pctdistance=0.8, autopct='%1.1f%%', colors=colors,textprops={'fontsize': 14,'fontfamily':'STXihei'},explode=explode)
        plt.title('情绪占比',fontsize=20,fontfamily='KaiTi')

        plt.legend(loc='lower right')

        # 保存图像
        save_path=dest_path
        plt.savefig(save_path)
        # plt.savefig("情绪占比饼状图\\"+png_name+'.png')

    #画风险折线图
    #输入的键值对为 月份：风险等级
    def __plot_risk_rank(self,user_name,risk_month,folder_path="风险等级折线图"):
        month_list=risk_month.keys()
        risk_rank=risk_month.values()
        plt.figure(figsize=(10, 10))
        plt.plot(month_list,risk_rank,marker='*')
        plt.grid(True)

        
        user_name_index=user_name.rfind('\\')
        if user_name_index !=-1:
            user_name=user_name[user_name_index+1:]
        plt.title(f"用户“{user_name}”的风险折线图",fontsize=20,fontfamily='KaiTi')
        plt.xlabel("月份")
        plt.ylabel("风\n险\n等\n级",rotation=0,fontsize=15,fontfamily='KaiTi')
        plt.xticks(rotation=270)
        plt.yticks([0,1,2,3])
        # plt.savefig()
        os.makedirs(folder_path, exist_ok=True)
        # 保存图像
        save_path=folder_path+'\\'+user_name+'.png'
        # print(save_path)
        plt.savefig(save_path)

    # 给定按月划分的微博文本txt目录，目录以用户名命名，生成用户风险折线图。
    # 文件路径：用户名/['202301.txt','202302.txt']
    def get_risk_rank_plot(self,src_path,min_len=1,dest_folder_path='风险等级折线图'):
        risk_month={}
        #提取用户名
        index1=src_path.rfind('\\')
        index1=max(index1,-1)

        user_name=src_path[index1+1:]
        text_file_paths=os.listdir(src_path)
        #按时间升序排序
        text_file_paths=sorted(text_file_paths)
        # 分别对每个月的文本进行风险评估
        for text_file_path in text_file_paths:
             # 进行风险评估
            risk_rank=self.risk_assessment(src_path+'\\'+f'{text_file_path}',min_len=min_len)
            index1=text_file_path.rfind('_')
            if index1 <0:
                index1=0
            index2=text_file_path.rfind('.')
            #得到月份
            _month=text_file_path[index1+1:index2]
            risk_month[_month]=risk_rank
        #画风险折线图
        self.__plot_risk_rank(user_name=user_name,risk_month=risk_month,folder_path=dest_folder_path)

    #计算得到情绪占比标准差
    #得到最大值和最小非零值
    def __maxmin(self,pro_list):
        Max=0
        Min=1
        for i in pro_list:
            if i >0 and i<Min:
                Min=i
            if i>Max:
                Max=i 
        return Max,Min
    
    # 计算标准差的方法
    #归一化,传入一个字典
    def get_standard_deviation(self, pro_dict):
        
        # 获取字典中的值
        pro_values = pro_dict.values()
        # 获取最大值和最小值
        pro_max, pro_min = self.__maxmin(pro_values)
        # 计算差值
        div = pro_max - pro_min
        # 如果差值为0，则将其设置为1，以避免除以0的错误
        if div == 0:
            div = 1
        # 对值进行归一化处理
        pro_values = [max((x - pro_min) / div, 0) for x in pro_values]
        # 计算均值
        mean_u = sum(pro_values) / len(pro_values)
        # 计算方差
        S_square = 0
        x_sum = 0
        for x in pro_values:
            x_sum += (x - mean_u) * (x - mean_u)
        S_square = x_sum / len(pro_values)
        # 计算标准差
        S = round(math.sqrt(S_square), 2)
        # 返回标准差
        return S
