from MyModel import Classification
from HaoChiUtils import DataAnalyzer as DA

if __name__=='__main__':
    # label_list=['快乐','恐惧','愤怒','惊讶','喜爱','厌恶','悲伤']
    #初始化模型
    myClassification=Classification("bert_model")
    #读取文本
    data = DA.get_dataList("cache\hhfxvbhxtjcckf_20230131 20230629 .txt")
    #预测
    pre=myClassification.get_predict_result(data)
    #打印预测结果
    print(pre)
    with open("模型示例.txt",'w') as f:
        for i in range(len(data)):
            st=f"文本：{data[i]}"+'\n'+f'预测情绪：{pre[i]}\n'
            f.write(st)





