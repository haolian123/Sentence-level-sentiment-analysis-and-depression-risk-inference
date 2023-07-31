from MyModel import Classification




if __name__=='__main__':
    myClassification=Classification("bert_model")
    print("++++++++++++++++++++++++++++++++++")
    data = ['如果情绪有天气，我困在阴天里','好想离开这个世界','讨厌下雨天','下雨天好烦','下雨天可以睡懒觉','怎样的我能让你更想念']
    myClassification.getPredictResult(data)
    print("++++++++++++++++++++++++++++++++++")
    myClassification.getPredictResult(data)