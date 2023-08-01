#导入相关的模块
import time
import os
import paddle
import paddlenlp as ppnlp
from paddlenlp.data import Stack, Pad, Tuple
import paddle.nn.functional as F
import numpy as np
from functools import partial #partial()函数可以用来固定某些参数值，并返回一个新的callable对象


class Classification:
    
    


    def __init__(self,load_path="bert_model") :
        #加载预训练模型Bert用于文本分类任务的Fine-tune网络BertForSequenceClassification, 它在BERT模型后接了一个全连接层进行分类。
        #由于本任务中的情感分类是多分类问题，设定num_classes为7
        self.__model = ppnlp.transformers.BertForSequenceClassification.from_pretrained("bert-base-chinese", num_classes=7)
        #调用ppnlp.transformers.BertTokenizer进行数据处理，tokenizer可以把原始输入文本转化成模型model可接受的输入数据格式。
        self.__tokenizer = ppnlp.transformers.BertTokenizer.from_pretrained("bert-base-chinese")
        #  加载：
        # load_path=model_path
        self.__load_path=load_path
        self.__model=self.__model.from_pretrained(self.__load_path)

        self.__tokenizer=self.__tokenizer.from_pretrained(self.__load_path)
        #数据预处理
    def __convert_example(self,example,tokenizer,label_list,max_seq_length=256,is_test=False):
        if is_test:
            text = example
        else:
            text = example['text']
            label=example['label']

        #tokenizer.encode方法能够完成切分token，映射token ID以及拼接特殊token
        encoded_inputs = tokenizer.encode(text=text, max_seq_len=max_seq_length)

        input_ids = encoded_inputs["input_ids"]
        segment_ids = encoded_inputs["token_type_ids"]

        if not is_test:
            label_map = {}
            for (i, l) in enumerate(label_list):
                label_map[l] = i

            label = label_map[label]
            label = np.array([label], dtype="int64")
            return input_ids, segment_ids, label
        else:
            return input_ids, segment_ids


    


    #预测函数
    def __predict(self,model, data, tokenizer, label_map, batch_size=1):
        examples = []
        for text in data:
            input_ids, segment_ids = self.__convert_example(text, tokenizer, label_list=label_map.values(),  max_seq_length=128, is_test=True)
            examples.append((input_ids, segment_ids))

        batchify_fn = lambda samples, fn=Tuple(Pad(axis=0, pad_val=tokenizer.pad_token_id), Pad(axis=0, pad_val=tokenizer.pad_token_id)): fn(samples)
        batches = []
        one_batch = []
        for example in examples:
            one_batch.append(example)
            if len(one_batch) == batch_size:
                batches.append(one_batch)
                one_batch = []
        if one_batch:
            batches.append(one_batch)

        results = []
        model.eval()
        for batch in batches:
            input_ids, segment_ids = batchify_fn(batch)
            input_ids = paddle.to_tensor(input_ids)
            segment_ids = paddle.to_tensor(segment_ids)
            logits = model(input_ids, segment_ids)
            probs = F.softmax(logits, axis=1)
            idx = paddle.argmax(probs, axis=1).numpy()
            idx = idx.tolist()
            labels = [label_map[str(i)] for i in idx]
            results.extend(labels)
        return results
    
    #对外接口
    def get_predict_result(self,data):
        predictions = self.__predict(self.__model, data, self.__tokenizer, self.__label_map, batch_size=1)
        return predictions
    





    #==========================================类变量==================================================
    #标签   
    # __label_list = ['0', '1', '2', '3', '4', '5', '6']
    __label_map ={'0': '快乐', '1': '恐惧', '2': '愤怒', '3': '惊讶', '4': '喜爱', '5': '厌恶', '6': '悲伤'}

    # #调用ppnlp.transformers.BertTokenizer进行数据处理，tokenizer可以把原始输入文本转化成模型model可接受的输入数据格式。
    # __tokenizer = ppnlp.transformers.BertTokenizer.from_pretrained("bert-base-chinese")
 
    __load_path=''
    # #加载预训练模型Bert用于文本分类任务的Fine-tune网络BertForSequenceClassification, 它在BERT模型后接了一个全连接层进行分类。
    # #由于本任务中的情感分类是多分类问题，设定num_classes为7
    # __model = ppnlp.transformers.BertForSequenceClassification.from_pretrained("bert-base-chinese", num_classes=7)


    


    




    





