#项目功能调用接口
from MainModule import DRI 
from HaoChiUtils import DataAnalyzer as DA
from WeiboComments import WeiboCommentCrawler as WCC
import os
import math
import requests
class TextEmotionAnalyzer:
    WCC
    def __init__(self) :
        #加载模型
        self.dri=DRI("model\\bert_model")
    

    #传入一个用户的txt文本，将情绪预测结果和情绪占比写入txt文本
    def sentiment_proportion(self,src_path,dest_path='情绪预测结果',min_len=1):
        # 创建文件夹
        os.makedirs(dest_path, exist_ok=True)
        #读取文本
        data=DA.get_dataList(src_path,min_len=min_len)
        #预测
        predictions=self.dri.myClassification.get_predict_result(data)
        #得到用户名
        index1=src_path.rfind('\\')
        index1=max(index1,-1)
        index2=src_path.rfind('.')
        # print('index1=',index1)
        # print('index2=',index2)
        user_name=src_path[index1+1:index2]

        dest_path+='\\'+user_name+'.txt'
        #得到情绪占比
        pro_dict=DA.calculate_label_proportions(predictions=predictions,label_list=self.dri.label_list)
        with open(dest_path,'w',encoding='utf-8') as f_write:
            write_dict=str(pro_dict)
            f_write.write("情绪占比：")
            f_write.write(write_dict+'\n\n')
            for i in range(len(data)):
                strs=f'({i+1}) 预测文本：{data[i]} \n预测情绪：{predictions[i]}\n\n'
                f_write.write(strs)


    #传入一个用户的txt文本，得到情绪占比饼状图
    def sentiment_ratio_pie(self,src_path,folder_path='情绪占比饼状图',min_len=1):
        #读取文本
        data=DA.get_dataList(src_path,min_len=min_len)
        pro_dict=self.dri.get_pro_dict(data)
        # 创建文件夹
        os.makedirs(folder_path, exist_ok=True)
        #提取用户名
        index1=src_path.rfind('\\')
        index1=max(index1,-1)
        index2=src_path.rfind('.')
        user_name=src_path[index1+1:index2]
        #图片保存路径
        dest_path=folder_path+'\\'+user_name+'.png'
        #画图
        self.dri.draw_pie(pro_dict,dest_path=dest_path)

    #传入一个用户的txt文本，得到预测的风险等级
    def risk_rank(self,src_path,min_len=1):
        rank=self.dri.risk_assessment(src_path,min_len=min_len)
        return rank

    #传入一个用户的txt文本文件夹，得到用户的风险等级折线图
    def risk_rank_plot(self,src_folder_path,dest_folder_path='风险等级折线图',min_len=1):
        self.dri.get_risk_rank_plot(src_path=src_folder_path,min_len=min_len,dest_folder_path=dest_folder_path)

    #传入一个用户的txt文本文件夹，得到用户的风险等级列表
    def risk_rank_list(self,src_folder_path,min_len=1):
        #得到文本文件列表
        text_list=os.listdir(src_folder_path)
        #按时间顺序升序排序
        text_list=sorted(text_list)
        res_rank_list=[]
        for text in text_list:

            rank=self.risk_rank(src_path=f'{src_folder_path}\\{text}',min_len=min_len)
            res_rank_list.append(rank)
        return res_rank_list


    #传入一个用户的txt文本，得到用户的情绪占比 key:values
    def  emotions_proportion(self,src_path,min_len=1):
         #读取文本
        data=DA.get_dataList(src_path,min_len=min_len)
        pro_dict=self.dri.get_pro_dict(data)
        return pro_dict
    
    
    #传入一个用户的txt文本文件夹，将情绪预测结果和情绪占比写入一个文件夹中
    def batch_sentiment_proportion(self,src_folder_path,dest_folder_path="情绪预测结果",min_len=1):
        text_list=os.listdir(src_folder_path)
        # 创建文件夹
        os.makedirs(dest_folder_path, exist_ok=True)
        for i in text_list:
            #得到文本文件的路径
            text_src_path=src_folder_path+'\\'+i
            #得到情绪预测结果
            self.sentiment_proportion(text_src_path,dest_folder_path,min_len=min_len)

    #传入一个包含多个用户文本文件夹的文件夹，得到所有用户的风险等级折线图
    def batch_risk_rank_plot(self,src_folder_path,dest_folder_path='风险等级折线图',min_len=1):
        #获取用户文件夹列表
        folder_list=os.listdir(src_folder_path)
        for folder_name in folder_list:
            #得到用户文件路径
            src_path=f'{src_folder_path}\\{folder_name}'
            #绘制折线图
            self.risk_rank_plot(src_folder_path=src_path,dest_folder_path=dest_folder_path,min_len=min_len)



    #传入一个包含多个用户文本的文件夹，得到所有用户的情绪占比饼状图
    def batch_sentiment_ratio_pie(self,src_folder_path,dest_folder_path='情绪占比饼状图',min_len=1):
        #获取用户文件夹列表
        user_text=os.listdir(src_folder_path)
        for user in user_text:
            src_path=f'{src_folder_path}\\{user}'
            self.sentiment_ratio_pie(src_path=src_path,folder_path=dest_folder_path)



    #风险评级
    #各项阈值
    # 近3、6、9个月风险等级平均值阈值
    # risk_mean_3=1.0769
    # risk_mean_6=1.5555
    # risk_mean_9=1.5333
    risk_mean_3=0.7719
    risk_mean_6=1.0238
    risk_mean_9=0.9012

    # 近3、6、9个月风险等级平均标准差阈值
    risk_S_3=0.81
    risk_S_6=0.8342
    risk_S_9=0.8582


    #给不同的时间段赋不同分数
    # 近3月：2分
    # 近6月：5分
    # 近9月：8分
    score_3=2
    score_6=5
    score_9=8

    #根据传入的风险等级列表【按月份递减】和月份，计算得到近month个月的平均风险等级
    def __risk_mean(self,risk_list,month):
        if(len(risk_list)<month):
            return -1
        risk_sum=0
        Len=month 
        for i in range(Len):
            risk_sum+=risk_list[i]

        return round(risk_sum/Len,4)
        
    #根据传入的风险等级列表【按月份递减】和月份，计算得到近month个月的风险等级标准差
    def __risk_S(self,risk_list,month):
        #月份不够、跳过
        if(len(risk_list)<month):
            return -1
        risk_sum=0
        Len=month 
        for i in range(Len):
            risk_sum+=risk_list[i]
        #得到平均值
        x_mean=risk_sum/Len 
        S_squre=0
        for i in range(Len):
            S_squre+=(risk_list[i]-x_mean)*(risk_list[i]-x_mean)
        return math.sqrt(S_squre/Len)

    #将平均值和标准差与阈值比较，返回应该加上的分数
    def __S_mean_cmp_score(self,S_m,mean_m,score_m,S_threshold,mean_threshold):
        if S_m==-1 or mean_m==-1:
            return 0
        
        #====================2023.8版本======================
        # 平均值超过，标准差不超过阈值：得到80%分数
        # 标准差超过，平均值不超过阈值：得到40%分数
        # 都超过，得到100%分数
        if mean_m>mean_threshold and  S_m<S_threshold:
            return score_m*0.8
        elif mean_m< mean_threshold and S_m > S_threshold:
            return score_m*0.4
        elif mean_m>mean_threshold and S_m>S_threshold :
            return score_m
        else:
            return 0
        #=================================================

        # #===================2023.9.13更新版本==============
        # score=score_m
        # if mean_m>=mean_threshold and S_m <= S_threshold:
        #     pass 
        # elif mean_m>=mean_threshold and S_m >S_threshold:
        #     score*=0.8
        # elif mean_m<=mean_threshold and S_m <S_threshold:
        #     score*=0.4
        # elif S_m>S_threshold and mean_m < mean_threshold:
        #     score=0
        # return score
        # #===================================================


    #赋分函数
    def __score_weighting(self,score_3,score_6,score_9):
        return score_3,score_6,score_9
    #传入一个按月份递增的风险等级列表，计算得到用户的风险分数
    def __risk_score(self,risk_list):
        #逆序，按月份递减
        risk_list_desc=list(reversed(risk_list))
        #得到近3、6、9个月的平均值、标准差
        mean_3=self.__risk_mean(risk_list_desc,3)
        mean_6=self.__risk_mean(risk_list_desc,6)
        mean_9=self.__risk_mean(risk_list_desc,9)
        S_3=self.__risk_S(risk_list_desc,3)
        S_6=self.__risk_S(risk_list_desc,6)
        S_9=self.__risk_S(risk_list_desc,9)
        score_3=self.__S_mean_cmp_score(S_3,mean_3,self.score_3,self.risk_S_3,self.risk_mean_3)
        score_6=self.__S_mean_cmp_score(S_6,mean_6,self.score_6,self.risk_S_6,self.risk_mean_6)
        score_9=self.__S_mean_cmp_score(S_9,mean_9,self.score_9,self.risk_S_9,self.risk_mean_9)
        #赋分
        score_3,score_6,score_9=self.__score_weighting(score_3,score_6,score_9)
        # 得到最终的分数
        score=score_3+score_6+score_9
        return score 
    
    #根据得到的分数进行风险评级
    def __risk_rating(self,score):
        if score>=0 and score<5:
            #低风险
            return 0
        if score>=5 and score<10:
            #中风险
            return 1
        if score >=10:
            #高风险
            return 2
        

    #主接口，传入用户各月份的文件夹，得到用户的风险评估级别

    def risk_level_assessment(self,src_folder_path,min_len=6):
        risk_list=self.risk_rank_list(src_folder_path=src_folder_path,min_len=min_len)
        score=self.__risk_score(risk_list=risk_list)
        return self.__risk_rating(score)
    


    #爬虫接口
    #传入一个用户uid，爬取用户的文本

    def user_month_comments(self,user_id,time_counter=9):
        Session = requests.session()
        # WCC.save_file_months(user_id=user_id,save_folder_path=save_folder_path,time_counter=time_counter,session=Session)
        wcc=WCC(user_id,time_counter)
        return wcc.get_data(Session)
    #获取用户uid列表

    def __get_uid_list(self,src_path):
        res_list=[]
        with open(src_path,'r') as f:
            for line in f:
                line=line.strip()
                if(len(line)>0):
                    res_list.append(line)

        return res_list
    
    # #指定一个用户uid文件，得到所有用户的文本
    # @classmethod
    # def batch_user_month_comments(self,src_path,save_folder_path,time_counter=9):
    #     uid_list=self.__get_uid_list(src_path=src_path)
    #     for uid in uid_list:
    #          self.user_month_comments(save_folder_path=f"{save_folder_path}",user_id=uid,time_counter=time_counter)


    #输入一个用户的UID，得到风险等级

    def assess(self,uid,count=9,min_len=2):
        #定义爬取对象
        user_text_path=self.user_month_comments(uid,count)
        risk_dict={0:'无风险',1:"低风险",2:"高风险"}
        # print(user_text_path)
        level=self.risk_level_assessment(src_folder_path=user_text_path,min_len=min_len)
        print(f"   用户{uid}  的风险等级为：{risk_dict[level]}")
        #还需要输出啥在下面加



