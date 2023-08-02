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

    dri.get_risk_rank_plot("走饭",6)
    
    # # print(res1s)
    # data=DA.get_dataList("D:\学习资料\CCCCAI\走饭\走饭_2012-03.txt",min_len=6)
    # pre=dri.myClassification.get_predict_result(data)
    # with open("走饭2.txt",'w') as f:
    #     for i in range(len(data)):
    #         strs=f'{data[i]}'+'\n'+f'{pre[i]}'+'\n'
    #         f.write(strs)






