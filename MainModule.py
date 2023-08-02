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
    __result1_threshold= 57.75
    # 熵率的阈值
    __entropy_threshold=0.0752


    __score1=__result1_threshold
    __score2=__score1+(130*0.7-__score1)/3
    __score3=__score2+(130*0.7-__score2)/3

    
    #情绪标签
    __label_list=['快乐','恐惧','愤怒','惊讶','喜爱','厌恶','悲伤']

    
    def __init__(self,model_path="bert_model"):
        #加载模型
        self.myClassification=Classification(model_path)

    #计算结果1
    #传入标签占比，保留2位小数
    def get_result1(self,pro_dict):
        # label_list=['快乐','恐惧','愤怒','惊讶','喜爱','厌恶','悲伤']
        weight_list=[-1,0.5,1,0,-1.5,0.5,1.3]
        result=0
        for i in range(len(self.__label_list)):
            result+=pro_dict[self.__label_list[i]]*weight_list[i]*100
        return round(result,2)
    

    #计算熵率
    #传入标签占比,保留5位小数
    def get_entropy(self,pro_dict,time_interval=20):
        # label_list=['快乐','恐惧','愤怒','惊讶','喜爱','厌恶','悲伤']
        total_pi=0
        for i in range(len(self.__label_list)):
            pi=pro_dict[self.__label_list[i]]
            # print(pi)
            if pi >0:
                total_pi+=-pi*math.log2(pi)
        return round(total_pi/time_interval,5)

    #得到占比标签
    #data 为待预测的数据
    def get_pro_dict(self,data):
        pre_list=self.myClassification.get_predict_result(data)
        pro_dict=DA.calculate_label_proportions(pre_list,label_list=self.__label_list)
        return pro_dict
    
    #得到情绪稳态
    # 情绪稳态：找pi最低的情绪，看有没有大它20%以上的情绪存在，
    # 有，情绪稳态=true，无，情绪稳态=false
    def get_emotional_homeostasis(self,pro_dict,threshold=0.2):
        min_pi=1
        max_pi=0
        for i in self.__label_list:
            if pro_dict[i]<min_pi and i !='惊讶' and pro_dict[i]>0:
                min_pi=pro_dict[i]
            if pro_dict[i]>max_pi and i !='惊讶' and pro_dict[i]>0:
                max_pi=pro_dict[i]
        if max_pi-min_pi>threshold:
            return True 
        return False
        # if max_pi-min_pi>threshold:
        #     return True 
        # return False
        
    # def judge_rank(self,score):


    #风险评估
    def risk_assessment(self,user_path="",min_len=1,draw_pie=True):
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
        print(pro_dict)
        if draw_pie:
            #画情绪占比饼图
    
            index1=user_path.rfind('\\')
            index2=user_path.rfind('_')
            user_name=user_path
            if index1>=0 and index2 >=0:
                user_name=user_path[index1:index2]
            
            # print(user_name)
            self.__draw_pie(pro_dict=pro_dict,png_name=user_name)
        score=0
        print("result1=",result1)
        #风险评估
        if result1 < self.__result1_threshold:
            
            return 0
        elif emotional_homeostasis==True and entropy>=self.__entropy_threshold:
            score=result1*1.2
        elif emotional_homeostasis==False and entropy<self.__entropy_threshold:
            score=result1*0.8
        else:
            score=result1
        
        risk_level=self.judge_rank(score)
        print("分数=",score)
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
    def __draw_pie(self,pro_dict,png_name,folder_path="情绪占比饼状图"):
        labels = list(pro_dict.keys())
        probs = list(pro_dict.values())

        # 自定义颜色列表
        # colors = ['skyblue', 'lightgreen', 'lightcoral', 'orange', 'pink', 'lightgrey', 'gold']
        # colors = ['red', 'orange', 'yellow', 'violet', 'blue', 'indigo','green']
        colors = ['#FF6347', '#FFD700', '#FFFF00', '#32CD32', '#B0E0E6', '#6495ED', '#9932CC']
        # colors = cm.GnBu(np.arange(len(labels),0,-2) / len(labels))
        # 自定义偏移量列表
        explode = (0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1)
        plt.figure(figsize=(10, 7),facecolor='lightgray')
        # 设置标签字体属性
        plt.pie(probs, labels=labels,pctdistance=0.8, autopct='%1.1f%%', colors=colors,textprops={'fontsize': 14,'fontfamily':'STXihei'},explode=explode)
        plt.title('情绪占比',fontsize=20,fontfamily='KaiTi')

        plt.legend(loc='lower right')
        # 创建文件夹
        os.makedirs(folder_path, exist_ok=True)

        # 保存图像
        save_path=folder_path+'\\'+png_name+'.png'
        plt.savefig(save_path)
        # plt.savefig("情绪占比饼状图\\"+png_name+'.png')

    #画风险折线图
    #输入的键值对为 月份：风险等级
    def __plot_risk_rank(self,user_name,risk_month,folder_path="风险等级折线图"):
        month_list=risk_month.keys()
        risk_rank=risk_month.values()
        plt.figure(figsize=(10, 6.5),facecolor='lightgray')
        plt.plot(month_list,risk_rank,marker='*')

        

        plt.title(f"用户“{user_name}”的风险折线图",fontsize=20,fontfamily='KaiTi')
        plt.xlabel("月份")
        plt.ylabel("风险等级")
        plt.xticks(rotation=45)
        plt.yticks([0,1,2,3])
        # plt.savefig()
        os.makedirs(folder_path, exist_ok=True)
        # 保存图像
        save_path=folder_path+'\\'+user_name+'.png'
        # print(save_path)
        plt.savefig(save_path)

    # 给定按月划分的微博文本txt目录，目录以用户名命名，生成用户风险折线图。
    # 文件路径：用户名/['202301.txt','202302.txt']
    def get_risk_rank_plot(self,user_name,min_len=0):
        risk_month={}
        text_file_paths=os.listdir(user_name)
        for text_file_path in text_file_paths:
            risk_rank=self.risk_assessment(user_name+'\\'+f'{text_file_path}',draw_pie=False,min_len=min_len)
            risk_month[text_file_path]=risk_rank
        self.__plot_risk_rank(user_name=user_name,risk_month=risk_month,folder_path=f"风险等级折线图")


