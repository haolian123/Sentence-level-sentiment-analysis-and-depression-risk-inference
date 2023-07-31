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
        #  加载：
        # load_path=model_path
        self.load_path=load_path
        self.model=self.model.from_pretrained(self.load_path)

        self.tokenizer=self.tokenizer.from_pretrained(self.load_path)
        #数据预处理
    def convert_example(self,example,tokenizer,label_list,max_seq_length=256,is_test=False):
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


    #数据迭代器构造方法
    def create_dataloader(self,dataset, trans_fn=None, mode='train', batch_size=1, use_gpu=True, pad_token_id=0, batchify_fn=None):
        if trans_fn:
            # dataset = dataset.apply(trans_fn, lazy=True)
            # dataset = paddle.io.Dataset.from_list(dataset)
            dataset = dataset.map(trans_fn, lazy=True)

        if mode == 'train' and use_gpu:
            sampler = paddle.io.DistributedBatchSampler(dataset=dataset, batch_size=batch_size, shuffle=True)
        else:
            shuffle = True if mode == 'train' else False #如果不是训练集，则不打乱顺序
            sampler = paddle.io.BatchSampler(dataset=dataset, batch_size=batch_size, shuffle=shuffle) #生成一个取样器
        dataloader = paddle.io.DataLoader(dataset, batch_sampler=sampler, return_list=True, collate_fn=batchify_fn)
        return dataloader


    #预测函数
    def predict(self,model, data, tokenizer, label_map, batch_size=1):
        examples = []
        for text in data:
            input_ids, segment_ids = self.convert_example(text, tokenizer, label_list=label_map.values(),  max_seq_length=128, is_test=True)
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
    
    def getPredictResult(self,data):
        predictions = self.predict(self.model, data, self.tokenizer, self.label_map, batch_size=32)
        for idx, text in enumerate(data):
            print('预测文本{}:{} \n预测情绪: {}\n'.format(idx+1,text, predictions[idx]))
    #==========================================类变量==================================================
    #标签   
    label_list = ['0', '1', '2', '3', '4', '5', '6']
    label_map ={'0': '快乐', '1': '害怕', '2': '生气', '3': '惊喜', '4': '喜爱', '5': '厌恶', '6': '难过'}
    #调用ppnlp.transformers.BertTokenizer进行数据处理，tokenizer可以把原始输入文本转化成模型model可接受的输入数据格式。
    tokenizer = ppnlp.transformers.BertTokenizer.from_pretrained("bert-base-chinese")
    #使用partial()来固定convert_example函数的tokenizer, label_list, max_seq_length, is_test等参数值
    trans_fn = partial(convert_example, tokenizer=tokenizer, label_list=label_list, max_seq_length=128, is_test=False)
    batchify_fn = lambda samples, fn=Tuple(Pad(axis=0,pad_val=tokenizer.pad_token_id), Pad(axis=0, pad_val=tokenizer.pad_token_id), Stack(dtype="int64")):[data for data in fn(samples)]
    


    #加载预训练模型Bert用于文本分类任务的Fine-tune网络BertForSequenceClassification, 它在BERT模型后接了一个全连接层进行分类。
    #由于本任务中的情感分类是多分类问题，设定num_classes为7
    model = ppnlp.transformers.BertForSequenceClassification.from_pretrained("bert-base-chinese", num_classes=7)


    


    




    





# data=[]
# # with open ("样例.txt",'r')as f:
# #     for line in f:
# #         line=line.strip("\n")
# #         data.append(line)
# # print(data)
# data = ['如果情绪有天气，我困在阴天里','好想离开这个世界','讨厌下雨天','下雨天好烦','下雨天可以睡懒觉','怎样的我能让你更想念']
# label_map ={'0': '快乐', '1': '害怕', '2': '生气', '3': '惊喜', '4': '喜爱', '5': '厌恶', '6': '难过'}

# predictions = predict(model, data, tokenizer, label_map, batch_size=32)
# for idx, text in enumerate(data):
#     print('预测文本{}:{} \n预测情绪: {}\n'.format(idx+1,text, predictions[idx]))