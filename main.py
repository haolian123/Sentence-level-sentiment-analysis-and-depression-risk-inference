from MyModel import Classification
from HaoChiUtils import DataAnalyzer as DA
from MainModule import DRI 
import os
from FunctionalInterface import TextEmotionAnalyzer as TEA

if __name__=='__main__':

    tea=TEA()


    ## ===============传入一个用户的txt文本，将情绪预测结果和情绪占比写入txt文本=======
    # src_path="D:\学习资料\CCCCAI\SuspectedDepressedUsers\hhfxvbhxtjcckf_20230131 20230629 .txt"
    # dest_path="D:\学习资料\CCCCAI\输出文件夹"
    # tea.sentiment_proportion(src_path,dest_path)


    # # ==============传入一个用户的txt文本，得到情绪占比饼状图===============
    # src_path="低级普男_2023-06.txt"
    # tea.sentiment_ratio_pie(src_path)

    # # =================传入一个用户的txt文本，得到预测的风险等级==============
    # src_path="D:\学习资料\CCCCAI\SuspectedDepressedUsers\hhfxvbhxtjcckf_20230131 20230629 .txt"
    # rank=tea.risk_rank(src_path)
    # print(rank)

    # ===========传入一个用户的txt文本文件夹，得到用户的风险等级列表==========
    src_path="D:\学习资料\CCCCAI\疑似用户\shsjxhdjxjd"
    rank=tea.risk_rank_list(src_path)
    print(rank)



    # =========传入一个用户的txt文本文件夹，得到用户的风险等级折线图===========
    src_path='D:\学习资料\CCCCAI\正常用户\便利店在逃关東煮·o·'
    tea.risk_rank_plot(src_folder_path=src_path)


    # ======传入一个用户的txt文本文件夹，将情绪预测结果和情绪占比写入一个文件夹中=========
    src_path='D:\学习资料\CCCCAI\正常用户\便利店在逃关東煮·o·'
    tea.batch_sentiment_proportion(src_path)

    # ==========传入一个包含多个用户文本文件夹的文件夹，得到所有用户的风险等级折线图=======
    src_path='D:\学习资料\CCCCAI\正常用户'
    tea.batch_risk_rank_plot(src_path,dest_folder_path='batch风险等级折线图')

    # ============传入一个包含多个用户文本的文件夹，得到所有用户的情绪占比饼状图=========
    src_path='D:\学习资料\CCCCAI\正常用户\便利店在逃关東煮·o·'
    tea.batch_sentiment_ratio_pie(src_folder_path=src_path)

    




    

