from MyModel import Classification
from HaoChiUtils import DataAnalyzer as DA



if __name__=='__main__':
    myClassification=Classification("bert_model")
    print("++++++++++++++++++++++++++++++++++")
    data = DA.get_dataList("样例.txt")
    print(data)
    pre=myClassification.getPredictResult(data)
    print(pre)
