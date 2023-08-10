from MyModel import Classification
from HaoChiUtils import DataAnalyzer as DA
from MainModule import DRI 
import os
from FunctionalInterface import TextEmotionAnalyzer as TEA

if __name__=='__main__':

    tea=TEA()


    ## ===============传入一个用户的txt文本，将情绪预测结果和情绪占比写入txt文本=======
    # src_path="SuspectedDepressedUsers\hhfxvbhxtjcckf_20230131 20230629 .txt"
    # dest_path="输出文件夹"
    # tea.sentiment_proportion(src_path,dest_path)


    # # ==============传入一个用户的txt文本，得到情绪占比饼状图===============
    # src_path="低级普男_2023-06.txt"
    # tea.sentiment_ratio_pie(src_path)

    # # =================传入一个用户的txt文本，得到预测的风险等级==============
    # src_path="SuspectedDepressedUsers\hhfxvbhxtjcckf_20230131 20230629 .txt"
    # rank=tea.risk_rank(src_path)
    # print(rank)
    # dest_path='风险用户预测结果'
    # user_name='shsjxhdjxjd'
    # # ===========传入一个用户的txt文本文件夹，得到用户的风险等级列表==========
    # src_path=f'风险用户\\{user_name}'
    # rank=tea.risk_rank_list(src_path)
    # print(rank)


    
    # # =========传入一个用户的txt文本文件夹，得到用户的风险等级折线图===========
    # src_path=f'风险用户\\{user_name}'
    # tea.risk_rank_plot(src_folder_path=src_path,dest_folder_path=f'风险用户预测结果\\{user_name}')


    # # ======传入一个用户的txt文本文件夹，将情绪预测结果和情绪占比写入一个文件夹中=========
    # src_path=f'风险用户\\{user_name}'
    # tea.batch_sentiment_proportion(src_path,f'风险用户预测结果\\{user_name}')

    # ==========传入一个包含多个用户文本文件夹的文件夹，得到所有用户的风险等级折线图=======
    # src_path='测试数据\8.5\yyz_cache'
    # tea.batch_risk_rank_plot(src_path,dest_folder_path='结果\\风险等级折线图8.5\\风险用户')

    # # ============传入一个包含多个用户文本或一个用户多个文本的文件夹，得到所有用户的情绪占比饼状图=========
    # src_path=f'测试数据\\8.5\\yyz_cache\\ammm18'
    # tea.batch_sentiment_ratio_pie(src_folder_path=src_path,dest_folder_path=f'结果\\情绪占比饼状图8.5')

    




    
    # #用户风险评级
    # src_folder_path=f"测试数据\8.5\yyz_cache"
    # user_list=os.listdir(src_folder_path)
    # for user in user_list:
    #     level=tea.risk_level_assessment(src_folder_path=src_folder_path+'\\'+user)
    #     print(f"{user}的风险等级为：{lev]el}")



    ## 爬取文本
    # TEA.batch_user_month_comments(src_path="uids.txt",save_folder_path="用户爬取文本",time_counter=9)

    TEA.user_month_comments(save_folder_path="用户爬取文本",user_id="7249120863",time_counter=9)