#导入相关的模块
import time
import os
import paddle
import paddlenlp as ppnlp
from paddlenlp.data import Stack, Pad, Tuple
import paddle.nn.functional as F
import numpy as np
from functools import partial 
import logging
#禁止输出日志
logging.disable(logging.CRITICAL)

class Classification:
    
    

    #构造函数
    def __init__(self,load_path="bert_model") :
      
        #选择模型
        self.__model = ppnlp.transformers.BertForSequenceClassification.from_pretrained("bert-base-chinese", num_classes=7)
        #tokenizer可以把原始输入文本转化成模型model可接受的输入数据格式。
        self.__tokenizer = ppnlp.transformers.BertTokenizer.from_pretrained("bert-base-chinese")
        #  加载：
        # load_path=model_path
        self.__load_path=load_path
        self.__model=self.__model.from_pretrained(self.__load_path)

        self.__tokenizer=self.__tokenizer.from_pretrained(self.__load_path)
    #=========================================private方法==================================
    #数据预处理
    def __convert_example(self, example, tokenizer, label_list, max_seq_length=256, is_test=False):
        # 如果是测试数据，则直接使用example作为文本
        if is_test:
            text = example
        else:
            # 如果是训练或验证数据，则从example中获取文本和标签
            text = example['text']
            label = example['label']

        # 使用tokenizer对文本进行切分、映射token ID以及拼接特殊token
        encoded_inputs = tokenizer.encode(text=text, max_seq_len=max_seq_length)

        # 获取切分后的token ID和token类型ID
        input_ids = encoded_inputs["input_ids"]
        segment_ids = encoded_inputs["token_type_ids"]

        if not is_test:
            # 构建标签映射字典
            label_map = {}
            for (i, l) in enumerate(label_list):
                label_map[l] = i

            # 将标签映射为对应的索引
            label = label_map[label]
            # 将标签转换为numpy数组，并指定数据类型为int64
            label = np.array([label], dtype="int64")
            # 返回输入的token ID、token类型ID和标签
            return input_ids, segment_ids, label
        else:
            # 如果是测试数据，只返回输入的token ID和token类型ID
            return input_ids, segment_ids


    


    #预测函数
    def __predict(self, model, data, tokenizer, label_map, batch_size=1):
        # 创建一个空列表用于存储样本
        examples = []
        # 遍历输入的数据
        for text in data:
            # 将文本转换为模型可接受的输入格式
            input_ids, segment_ids = self.__convert_example(text, tokenizer, label_list=label_map.values(), max_seq_length=128, is_test=True)
            # 将转换后的样本添加到列表中
            examples.append((input_ids, segment_ids))

        # 定义一个函数用于将样本批量化
        batchify_fn = lambda samples, fn=Tuple(Pad(axis=0, pad_val=tokenizer.pad_token_id), Pad(axis=0, pad_val=tokenizer.pad_token_id)): fn(samples)
        # 创建一个空列表用于存储批次
        batches = []
        one_batch = []
        # 遍历样本列表
        for example in examples:
            # 将样本添加到当前批次中
            one_batch.append(example)
            # 如果当前批次大小达到指定的批次大小
            if len(one_batch) == batch_size:
                # 将当前批次添加到批次列表中
                batches.append(one_batch)
                # 重置当前批次
                one_batch = []
        # 如果还有剩余的样本，将其添加到批次列表中
        if one_batch:
            batches.append(one_batch)

        # 创建一个空列表用于存储预测结果
        results = []
        # 将模型设置为评估模式
        model.eval()
        # 遍历批次列表
        for batch in batches:
            # 将批次样本进行批量化处理
            input_ids, segment_ids = batchify_fn(batch)
            # 将输入转换为PaddlePaddle张量
            input_ids = paddle.to_tensor(input_ids)
            segment_ids = paddle.to_tensor(segment_ids)
            # 使用模型进行推理得到预测结果
            logits = model(input_ids, segment_ids)
            # 对预测结果进行softmax处理得到概率
            probs = F.softmax(logits, axis=1)
            # 获取概率最大的类别索引
            idx = paddle.argmax(probs, axis=1).numpy()
            idx = idx.tolist()
            # 将索引转换为对应的标签
            labels = [label_map[str(i)] for i in idx]
            # 将预测结果添加到结果列表中
            results.extend(labels)
        # 返回预测结果
        return results
    
    #=========================================对外接口===============================
    def get_predict_result(self,data):
        predictions = self.__predict(self.__model, data, self.__tokenizer, self.__label_map, batch_size=1)
        return predictions
    





    #==========================================类变量==================================================
    #标签   
    # __label_list = ['0', '1', '2', '3', '4', '5', '6']
    __label_map ={'0': '快乐', '1': '恐惧', '2': '愤怒', '3': '惊讶', '4': '喜爱', '5': '厌恶', '6': '悲伤'}

    #加载路径
    __load_path=''


    


    




    





