from MyModel import Classification
from HaoChiUtils import DataAnalyzer as DA
from MainModule import DRI 
import os
if __name__=='__main__':
    # # label_list=['快乐','恐惧','愤怒','惊讶','喜爱','厌恶','悲伤']
    # #初始化模型
    # myClassification=Classification("bert_model")
    # #读取文本
    # data = DA.get_dataList("cache\hhfxvbhxtjcckf_20230131 20230629 .txt")
    # #预测
    # pre=myClassification.get_predict_result(data)
    # #打印预测结果
    # print(pre)
    # with open("模型示例.txt",'w') as f:
    #     for i in range(len(data)):
    #         st=f"文本：{data[i]}"+'\n'+f'预测情绪：{pre[i]}\n'
    #         f.write(st)


    # #得到风险等级
    dri=DRI()
    # fir_list=os.listdir("SuspectedDepressedUsers")
    # res1s=[]
    # print('======================')
    # for i in fir_list:
    #     user_path="SuspectedDepressedUsers\\"+i
    #     # pre=dri.myClassification.get_predict_result(data)
    #     print("用户：",i)
        
    #     print("风险等级：",dri.risk_assessment(user_path=user_path,min_len=6,draw_pie=False))
    #     # dri.risk_assessment(user_path=user_path,min_len=2,draw_pie=False)
    #     # break


    # #预测情绪
    # # print(res1s)
    # data=DA.get_dataList("D:\学习资料\CCCCAI\正常用户\峰哥亡命天涯\峰哥亡命天涯_2023-03.txt",min_len=6)
    # pre=dri.myClassification.get_predict_result(data)
    # with open("老逼灯.txt",'w') as f:
    #     for i in range(len(data)):
    #         strs=f'{data[i]}'+'\n'+f'{pre[i]}'+'\n'
    #         f.write(strs)




    #画风险等级折线图
    dri=DRI()

    file_name="正常用户" #文件夹名字
    users=os.listdir(file_name)# 获取文件列表
    for i in users:
        #画风险等级折线图
        dri.get_risk_rank_plot("正常用户\\"+i,min_len=6)




