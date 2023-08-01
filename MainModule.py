#项目主模块
from HaoChiUtils import DataAnalyzer as DA
from MyModel import Classification
#Depression risk inference
class DRI:
    def __init__(self,model_path="bert_model") -> None:
        self.myClassification=Classification(model_path)


    #

