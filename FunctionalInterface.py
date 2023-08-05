#项目功能调用接口
from MainModule import DRI 
from HaoChiUtils import DataAnalyzer as DA
import os
import math
class TextEmotionAnalyzer:
    def __init__(self) :
        #加载模型
        self.dri=DRI("bert_model")
    

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

