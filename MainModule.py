#项目主模块
from HaoChiUtils import DataAnalyzer as DA
from MyModel import Classification
import math
#Depression risk inference
class DRI:
    #结果1的阈值
    __result1_threshold=59.89
    # 熵率的阈值
    __entropy_threshold=0.08014

    __label_list=['快乐','恐惧','愤怒','惊讶','喜爱','厌恶','悲伤']
    def __init__(self,model_path="bert_model"):
        #加载模型
        self.myClassification=Classification(model_path)

    #计算结果1
    #传入标签占比，保留2位小数
    def get_result1(self,pro_dict):
        # label_list=['快乐','恐惧','愤怒','惊讶','喜爱','厌恶','悲伤']
        weight_list=[-1,0.5,1,0,-1.5,0.5,1.3]
        result=0
        for i in range(len(self.__label_list)):
            result+=pro_dict[self.__label_list[i]]*weight_list[i]*100
        return round(result,2)
    

    #计算熵率
    #传入标签占比,保留5位小数
    def get_entropy(self,pro_dict,time_interval=20):
        # label_list=['快乐','恐惧','愤怒','惊讶','喜爱','厌恶','悲伤']
        total_pi=0
        for i in range(len(self.__label_list)):
            pi=pro_dict[self.__label_list[i]]
            # print(pi)
            if pi >0:
                total_pi+=-pi*math.log2(pi)
        return round(total_pi/time_interval,5)

    #得到占比标签
    #data 为待预测的数据
    def get_pro_dict(self,data):
        pre_list=self.myClassification.get_predict_result(data)
        pro_dict=DA.calculate_label_proportions(pre_list,label_list=self.__label_list)
        return pro_dict
    
    #得到情绪稳态
    # 情绪稳态：找pi最低的情绪，看有没有大它10%以上的情绪存在，
    # 有，情绪稳态=true，无，情绪稳态=false
    def get_emotional_homeostasis(self,pro_dict):
        min_pi=1
        max_pi=0
        for i in self.__label_list:
            if pro_dict[i]<min_pi and i !='惊讶':
                min_pi=pro_dict[i]
            if pro_dict[i]>max_pi and i !='惊讶':
                max_pi=pro_dict[i]
        if max_pi-min_pi>0.1:
            return True 
        return False
        
    # def judge_rank(self,score):


    #风险评估
    def risk_assessment(self,user_path="",min_len=0):
        #待预测文本列表
        data_list=DA.get_dataList(user_path,min_len=min_len)
        #情绪占比
        pro_dict=self.get_pro_dict(data_list)
        #熵率
        entropy=self.get_entropy(pro_dict)
        #结果1
        result1=self.get_result1(pro_dict)
        #稳态
        emotional_homeostasis=self.get_emotional_homeostasis(pro_dict)

if __name__=='__main__':
    dri=DRI()
    data=DA.get_dataList("D:\学习资料\CCCCAI\SuspectedDepressedUsers\_壹然__20230407 20230721 .txt",min_len=2)
    # pre=dri.myClassification.get_predict_result(data)
    pro_dict=dri.get_pro_dict(data)
    en=dri.get_entropy(pro_dict)
    res1=dri.get_result1(pro_dict)
    print(pro_dict)
    print(en)
    print("res1=",res1)
    print(dri.get_emotional_homeostasis(pro_dict=pro_dict))




    # with open("zoufan.txt",'w') as f:
    #     for i in range(len(data)):
    #         strs=f'{data[i]}'+'\n'+f'{pre[i]}'+'\n'
    #         f.write(strs)
