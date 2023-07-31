###########################################################
'''
一个工具类:
    1.getDataList():将txt文本中的数据集转化为列表
'''


class Utils:
    def __init__(self) -> None:
        pass

    #转化为列表可供模型读取
    #data_file_path:    文件路径
    #min_len:           文本的最小长度
    @classmethod
    def getDataList(self,data_file_path,min_len=0):
        ret_list=[]
        with open(data_file_path,'r',encoding='utf-8') as f:
            for data_line in f:
                data_line=data_line.strip().strip('\n')
                ##文本清洗：删除@或url等无关信息
                #需要嵌入代码


                if data_line is not None and len(data_line) >min_len:
                    ret_list.append(data_line)
        return ret_list
    
