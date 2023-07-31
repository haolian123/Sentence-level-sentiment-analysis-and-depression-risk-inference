from MyModel import Classification
from utils import Utils



if __name__=='__main__':
    myClassification=Classification("bert_model")
    print("++++++++++++++++++++++++++++++++++")
    data = Utils.getDataList("样例.txt")
    pre=myClassification.getPredictResult(data)
    print(pre)