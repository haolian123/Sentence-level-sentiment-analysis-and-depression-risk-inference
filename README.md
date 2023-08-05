# CCCCAI

## 爬虫函数相关文件说明

### WeiboComments.py

#### 一、主要参数说明：
##### 爬虫通用参数：
+ `header`：作为请求头的一部分进行操作：
  我们使用`fake_useragent`库进行相关操作：`"User-Agent": UserAgent().random`使得请求头随机化代理，防止ip被封禁

+ `url`：获取网页请求文件内容的协议串：
  在微博中有具体api接口供访问，在访问用户个人空间时和`uid`、`container_id`、`l_fid`、`since_id`密不可分，例如：`https://m.weibo.cn/api/container/getIndex?uid={}&luicode=10000011&lfid={}&type=uid&value={}&containerid={}&since_id={}`

##### 微博使用的api参数：
+ `uid, user_id`：区分微博用户的唯一数字标识，其链接常呈现`https://m.weibo.cn/u/{uid}`的形式

+ `container_id, contain_id`：在获取响应JS文件时在url中必要的数字标识，通常格式为：`107603{uid}`

+ `l_fid`：在获取响应JS文件时在url中必要的数字标识，通常格式为：`107603{uid}`

+ `since_id, min_since_id, min_id`：获取具体微博条数的非必要参数（默认不填为第一页），其位置常在`https://m.weibo.cn/api/container/getIndex?uid={}&luicode=10000011&lfid={}&type=uid&value={}&containerid={}&since_id{}`（`since_id`为当前`url`位置）中的`data-cardlistInfo`（开发者环境下可以找到）

#### 二、相关函数说明：
##### 基本函数：
###### 1. ` __trans_time(self,v_str)`说明：
+ `v_str`为微博时间的格式：
  `mblog: {visible: {type: 0, list_id: 0}, created_at: "Fri Jul 21 15:05:48 +0800 2023", id: "4925957071442718",…}`
  转换为标准时间格式：`%Y-%m-%d %H:%M:%S`
+ 返回时间格式为上述标准时间格式

###### 2. `__get_since_id(self, header, user_id, l_id, contain_id, since_id)`说明：
+ 通过`url`访问具体文件（使用`requests.get`方式）：
   对内容进行`json`方式解析为键值对
+ 锁定`since_id`：
   其中，为确保我们访问途中不会发生报错，因此错误访问将会使得`since_id='404'`
+ 返回`str`型的`since_id`

###### 3. `__get_page(self, header, user_id, l_id, contain_id, since_id='')`说明：
+ 基本步骤同上一函数
+ 返回页面`json`键值对式的列表类型内容

###### 4. `__rebuild(self, data)`说明：
+ 筛除内容：
  通过正则表达式选择`r'<[^>]+>|转发微博'`，并使用`re`库中的`sub('',text_data)`将这些内容删除
+ 节选数据：
  微博用户的发言只存在于`data-cards-[list]-mblog-text`中，因此只需对这些内容进行上述操作，不为空部分将创建时间`created_at`和对应的`text_data`放入`li`
+ 输出内容`[['created_at',text_data]]`

##### 外部接口部分：
###### 1. `get_user_name(self, user_id=None, contain_id=None, header=__default_headers)`说明：
+ 用户名获取：
  通过另一`url`的api接口：`['data']['cards'][1]['mblog']['user']['screen_name']`
+ 输出`str`型`user_name`

###### 2. `save_file(self, filename, text)`说明：
+ 检测文件路径是否存在
+ 将数据逐行写入（`encoding='utf-8'`）
+ 输出文本（.txt类型）

##### 变种部分：
###### 1. `get_data(self, min_id='', user_id=None, l_id=None, contain_id=None, header=__default_headers)`说明：
+ 集成了`__get_page`和`__rebuild`的函数内容：
  将获取各页内容的获取及数据清洗部分集成，并且过滤了文本长度（筛除后）为空和大于50的文本，放入`li`列表中
+ 计时系统（待改进）：
  + `timing=''`：记录当前有效文本的`created_at`文本值
  + `last_time=''`：记录最新的`timing`值（发言截止时间）
  + `last_month=0`：记录截止发言月份
  + `temp_month=0`：记录当前读到的发言月份
  + `rest_month=0`：使用公式`rest_month=abs(last_month-temp_month)`进行差额时间计算【还是不太正确】
+ 输出数据：
  + 数据1：记录的列表型的`li`
  + 数据2：`str`型的`'yyyymmyyyymm'`（起始时间截止时间）

###### 2. `fetch_file(self, count=5, header=__default_headers, user_id=None, l_id=None, contain_id=None, since_id='')`说明：
+ 记录月份系统：
  + `count`：记录月份数
  + `len(row)!=0: count-=1`：非空数据时`-1`，防止因发言数为0而出错
+ 文件输出：
  文件名：【用户名】【上一函数的数据2】.txt

###### 3. `data_per_month(self, header=__default_headers, since_id='', user_id=None, l_id=None, contain_id=None, time_counter=None)`说明：
+ 由变种函数1改进，更新内容：
  + 参数：
    `month_id`：`list`型：记录已记录数据的时间（年月）列表
    `per_month`：`list`型：记录有效月份文本数据
  + 计时系统：
    `if temp_month != 0`：防止空月份
    `rest_month = (last_month - temp_month + 12) % 12`：使用约瑟夫问题算法计算差额月份
+ 增加内容：
  + 错误判断机制：
    ```
    if len(month_id) > len(text):
            month_id = month_id[::-1][1:]
<<<<<<< HEAD
    ```
=======
>>>>>>> 7b6c6a9b3c6cffd5bc8468cccd09490cbb7ee1da
  + 补全信息机制：末尾使用
    ```
    if len(per_month) != 0:
            li.append(per_month)
<<<<<<< HEAD
    ```
=======
>>>>>>> 7b6c6a9b3c6cffd5bc8468cccd09490cbb7ee1da
+ 数据输出：
  + 数据1：发言文本数据（按先后顺序）`list`类型
  + 数据2：记录年月列表，`list`类型

###### 4. `save_file_user(self, filename, text)`说明：
+ 输入：
  + `filename`：年份月份时间和用户文本的字串
  + `text`：`list`式用户发言文本数据
+ 输出：
  存储于`./{user_id}`的所有收集月份发言文本

###### 5. `save_file_months(self, header=__default_headers, user_ids=None, time_counter=None)`说明：
+ 输入：
  + `user_ids`：用户`uid`的列表集合
  + `time_counter`：月份跨越时间计数
+ 输出：
  + 使用函数`save_file_user`进行批量保存文本


## 文本处理文件

### HaoChiUtils.py

#### 一、主要参数说明：

##### 文本处理必要参数：
+ `__stop_terms`：指定的停用词，我们筛除一些固定的微博“无效文本”（这些文本不能代表用户情感需要）

+ `__stopwords=[]`：读取停用词表，通过`__init__`生成函数，我们将`hit_stopwords.txt`文件读入为`list`类型数据

#### 二、相关函数说明：

##### 文本预处理类 `DataPreprocess`
###### 1. `__init__`函数：
+ 功能：
  由`stopwords_file_path = "hit_stopwords.txt"`读入停用词表，生成`__stopwords`列表

###### 2. `text_clean`函数：
+ 参数介绍：
  + `keep_segmentation`：当值为`False`时，`text_clean`方法会使用`jieba`库对于清洗后的文本进行分词处理，并返回分词后的结果
  + `has_user_id`：表示当前文本是否含有用户id

+ 清洗步骤（主要使用正则方法`re`库）：
  1. 简繁转化：使用`cc=OpenCC('t2s')`函数将繁体中文转换为简体中文`cc.convert(text)`
  2. id去除：去除`id`后冒号的内容
  3. 去除网页链接
  4. 去除`@`用户和回复标记
  5. 去除表情符号
  6. 将文本符号转换为空格
  7. 去除数字
  8. 删除首尾空格
  9. 将表情符号转换为文本描述：
      使用`emoji`库的`emoji.demojize(text)`进行转化，之后使用`jieba`库进行切词`jieba.cut(text,cut_all=False)`，在去除停用词后使用空格拼接字符串

###### 3. `text_process(self,input_file_path="DataSet.tsv", output_file_path="Clean_data.tsv")`函数：
+ 参数介绍：
  + `count`：正在处理信息条数
  + `cleaned_lines`：完成再处理的数据

+ 主要功能：
  遍历已处理的文本内容，检查列长度是否满足条件，删去第一列内容为空的行

+ 输出：
  将记录写入路径`output_file_path="Clean_data.tsv"`中

##### 数据分析类 `DataAnalyzer`
###### 1. `split_dataSet(self,dataSet_path='dataSet.tsv')`函数：
+ 功能：
  读取数据集，划分训练集和测试集，划分验证集和测试集，并保存划分后的数据集：train.tsv、eval.tsv 和 test.tsv

###### 2. `draw_process(self, title='trainning acc', color='r', iters=[], data=[], label='trainning acc', png_path='plot')`函数：
+ 功能：
  将训练数据结果记录在图像上，并且保存图像

###### 3. `calculate_label_proportions(self,predictions,label_list)`函数：
+ 参数介绍：
  + `prediction_dict={}`：创建字典用于保存情绪结果和其数量
  + `total_cnt=0`：记录条数总量
  + `res_dict={}`：创建字典用于存储标签及对应占比

+ 主要功能：
  记录预测的结果和其对应的情绪标签，并且计算其占比

+ 输出：
  返回情绪标签及其情绪预测占比的字典

###### 4. `get_dataList(self,data_file_path,min_len=0)`函数：
+ 功能：
  用于文本文件转化为列表供模型读取

+ 输出：
  `ret_list`的`list`数据，作为外部接口关联

## 模型代码

### MyModel.py

#### 一、主要参数：

#### 二、相关函数说明：

##### 1. `__init__(self,load_path="bert_model") `函数说明：
+ `self.__model = ppnlp.transformers.BertForSequenceClassification.from_pretrained("bert-base-chinese", num_classes=7)`：
  从`ppnlp`引入模型（飞桨的`nlp`）为文本转化为序列分类模型，`num_classes=7`将分类种类定为7

+ `self.__tokenizer = ppnlp.transformers.BertTokenizer.from_pretrained("bert-base-chinese")`：
  调用ppnlp.transformers.BertTokenizer进行数据处理，tokenizer可以把原始输入文本转化成模型model可接受的输入数据格式

+ `self.__model=self.__model.from_pretrained(self.__load_path)`：
  从`__load_path`加载模型进入

##### 2. `__convert_example(self,example,tokenizer,label_list,max_seq_length=256,is_test=False)`说明：
###### 参数
+ `example`：作为键值对存在存在两个键`text`和`label`的，而`is_test`使得`text=example`的意义为在测试中`example`就是文本

+ `encoded_inputs`：使用`tokenizer.encode`对`text`进行切分处理，得到键值对。在`is_test=True`情况下输出键值对仅有`input_ids`和`segment_ids`，不包括`label`（情感标签）

###### 主要功能
+ 将`example`中的键值对限制`max_seq_length`最大长度，切片完成后得到`encoded_inputs`，之后可以得到`label`、`input_ids`和`segment_ids`，并返回对应数据列表

##### 3. `__predict(self,model, data, tokenizer, label_map, batch_size=1)`说明：
###### 参数
+ `example`：将`(input_ids,segment_ids)`放入`list`类型的`example`
+ ·batchify_fn：由生成的元组`Pad`函数，并且将samples输入`lamda`的函数，`Pad`是一个张量转化函数
+ `one_batch`：充当将`examples`中的元组对放入列表的中转容器
+ `batches`：`batches`录入长度低于`batch_size`的`one_batch`的列表容器
+ `results`：模型预测各个标签的结果列表

###### 主要功能
+ 将`data`转换为可供模型处理的`batchers`键值对，将模型设置为评估模式，通过`model.eval() `实现

+ 将输入数据传入模型进行判断，得到输出的`logits`，之后利用`softmax()`函数进行概率归一化，得到类别概率分布

+ 使用`paddle.argmax()`函数找到最大概率对应的类别索引值，将其转换为`numpy`的数组形式，并转换为`Python`的列表形式`idx.tolist()`

+ 将对应的标签拓展至`results`中

##### 4. `predictions = self.__predict(self.__model, data, self.__tokenizer, self.__label_map, batch_size=1)`说明：
+ 功能：
  将`data`进行重处理，返回`predictions`结果（上述的`results`）

## 工具类代码

### MainModule.py

#### 一、主要参数：

##### 各项参数：
+ `__result1_threshold= 57.75`：结果1的阈值
+ `__entropy_threshold=0.0752`：熵率的阈值
+ `__score1=__result1_threshold`
+ `__score2=__score1+(130*0.7-__score1)/3`
+ `__score3=__score2+(130*0.7-__score2)/3`
+ `label_list=['快乐','恐惧','愤怒','惊讶','喜爱','厌恶','悲伤']`：情绪标签设置

#### 二、相关函数说明：

##### 1. `__init__`函数说明：
+ 功能：
  生成类对象时，同时引入`MyModel`中`Classification`中的`bert_model`模型

### FunctionalInterface.py

#### 一、主要参数说明：

#####
