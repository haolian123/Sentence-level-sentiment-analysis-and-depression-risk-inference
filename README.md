# 项目概述

​	该项目利用人工智能技术，通过对社交平台用户近期的发文进行情感分析，使用设计的算法判断用户抑郁风险等级，并为其生成报告，报告中包含用户近 9 月抑郁风险折线图、用户抑郁风险等级、相关心理援助资源链接和专业建议。

​	该项目的意义是让国内社交平台用户以较为“无痛”的方式，更好地掌握自己的心理健康状态，便捷地寻求所需的专业心理援助。 

# 使用说明

## 运行环境

AI Studio 的BML lab V100 16GB版本

## 模型训练和保存

使用项目的功能前需要得到一个情绪分类模型，由于模型较超过了限制的文件大小，需要先运行文件夹ModelTraining中的BertMain.ipynb文件，通过训练获得模型。并将模型训练过程中产生的文件(如下)：

1. config.json
2. model_config.json
3. model_state.pdparams
4. special_tokens_map.json
5. tokenizer_config.json
6. vocab.txt

保存到main.py同路径下的bert_model文件夹中。

## 接口使用

爬取指定UID的微博文本并对其进行抑郁风险推断

```python
from FunctionalInterface import TextEmotionAnalyzer as TEA
if __name__=='__main__':
    tea=TEA()
    uid="7478209878"#测试用例
    tea.assess(uid)
```

# 代码文件说明

## 模型训练文件

## 爬虫函数相关文件说明

### WeiboComments.py

指定uid，爬取对应用户的文本。

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
    ```
```
  if len(per_month) != 0:
          li.append(per_month)
```
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

用于处理用户的文本的接口。

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

核心模型接口。

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

加载模型对数据进行预测和分析。

#### 一、主要参数：

##### 各项参数：
+ `__result1_threshold= 57.75`：结果1的阈值
+ `__entropy_threshold=0.0752`：熵率的阈值
+ `__score1=__result1_threshold`
+ `__score2=__score1+(130*0.7-__score1)/3`
+ `__score3=__score2+(130*0.7-__score2)/3`
+ `label_list=['快乐','恐惧','愤怒','惊讶','喜爱','厌恶','悲伤']`：情绪标签设置

#### 二、相关函数说明：

##### 1. `__init__(self,model_path="bert_model")`函数说明：
+ 功能：
  生成类对象时，同时引入`MyModel`中`Classification`中的`bert_model`模型

##### 2. `get_result1(self, pro_dict)`函数说明：
###### 相关参数说明：
+ `weight_list = [-1, 0.5, 1, 0, -1.5, 0.5, 1.3]`：对应上述的`label_list`值，作为计算得分的权重

###### 输出说明：
+ 此函数通过遍历键值对`pro_dict`的各类情感占比，得到得分`result`，再进行四舍五入得到小数点后保留两位的小数结果（负面情绪得分）

##### 3. `get_entropy(self, pro_dict, time_interval=20)`函数说明：
###### 相关参数：
+ `pi`：作为概率p_i出现，代表某一情绪的占比
+ `total_pi`：作为平均熵出现，按照信息熵计算方法`total_pi += -pi * math.log2(pi)`
+ `time_interval=20`：作为时间间隔的参数出现

###### 主要功能：
+ 功能：
  将`pi>0`的值输入至`total_pi`计算中，此方法通过遍历输入的`pro_dict`键值对实现

+ 输出：
  `total_pi/time_interval`（熵率）进行四舍五入得到的小数点后保留5位的小数结果

##### 4. `get_pro_dict(self, data)`函数说明：
###### 相关参数：
+ `data`：读入的用户发言文本列表

###### 主要功能
+ 输出：
  将`data`中的用户发言文本进行逐一预测，并计算返回`pro_dict`键值对中，最后输出这个情绪占比键值对

##### 5. `get_emotional_homeostasis(self, pro_dict, threshold=0.2)`函数说明：
###### 相关参数：
+ `pro_dict`：输入的一份情绪占比键值对
+ `threshold`：情绪比重的差值输入设置（用于寻找是否有相差比重较大的情绪）

###### 主要功能：
+ 输出：
  遍历情绪占比键值对`pro_dict`得到最大（最小）权重占比，之后输出`max_proportion - min_proportion > threshold`的布尔值
  注：因为“惊讶”情绪在`bert`模型中的判断适应性较差，因此此函数中针对“惊讶”的情绪并不计入比重

##### 6. `risk_assessment(self,user_path="",min_len=1,min_text_num=5)`函数说明：
###### 相关参数：
+ `min_len`：最小文本长度，`DA.get_dataList`函数使用此参数过滤长度在这之下的文本
+ `min_text_num`：最小文本条数，在结果判断时，为了可靠性考虑，因此要求其发言条数必须大于等于`min_text_num`，才能判断结果
+ `score`：风险得分

###### 主要功能：
+ 根据情绪波动校准：
  在“悲伤”情绪占比小于等于设置的悲伤占比值域`self.__sadness_proportion_threshold`时，判断其情绪标准差`S`是否大于情绪波动值域`__mood_change_threshold`范围，若低于此范围，那么将`result`（负面情绪得分）再减少10%，否则在原基础上增加10%得分

+ 风险得分计算：
  这里通过下述四分支系统进行计算（特殊情况处理）：
  1. `result1`低于设置的负面情绪得分阈值`__result1_threshold`或发言信息条数低于上述`min_text_num`值:
      其危险等级`risk_level`为0，因为此用户当月的情绪总体并不为负面，或者其发言条数不足以支撑我们得出结果
  2. 判断情绪存在较大占比差距（通过稳态`get_emotional_homeostasis`函数计算）且熵率大于等于熵率阈值`__entropy_threshold`：
      其风险得分为`result1*1.2`，证明该用户当月的心理状况复杂，且其熵率大于等于所设阈值
  3. 判断情绪并不存在较大差异，且熵率低于预设范围值：
      其风险得分为`result1*0.8`，证明该用户当月的情绪差异较小，且其熵率小于所设阈值
  4. `score=result1`：不属于我们划分的特殊情况，因此不做处理

+ 输出：
  风险等级判断使用类内函数`judge_rank(score)`，输出数字代表

##### 7. `judge_rank(self,score)`函数说明：
###### 功能：
+ 输出：
  根据参数`self.__score1, self.__score2, self.__score3`三个函数阈值进行分支输出四个等级：`0, 1, 2, 3`

##### 8. `draw_pie(self,pro_dict,dest_path)`函数说明：
###### 参数：
+ `pro_dict`：用户的各种情绪及占比键值对
+ `dest_path`：输出图片路径

###### 功能：
+ 输出：由`pro_dict`数据形成饼状图输出

##### 9. `__plot_risk_rank(self,user_name,risk_month,folder_path="风险等级折线图")`函数说明：
###### 主要参数：
+ `risk_month`：储存“月份：风险等级”的键值对序列

###### 功能：
+ 输出：用户在这几个月份的风险等级变化情况

##### 10. `__maxmin(self,pro_list)`函数说明：
###### 功能：
+ 输出：两个情绪列表最值

##### 11. `get_standard_deviation(self, pro_dict)`函数说明：
###### 功能：
+ 输出：返回情绪键值对值的标准差值（保留小数点后两位小数）

#### 三、集成函数说明：

##### 1. `get_risk_rank_plot(self,src_path,min_len=1,dest_folder_path='风险等级折线图')`函数说明：
###### 主要参数：
+ `risk_month={}`：与此类`__plot_risk_rank`的输入部分作用相同

###### 功能：
+ 输出：将按月划分的用户发言文本转换成对应月份的“风险等级折线图”

### FunctionalInterface.py

项目主要功能接口类。

#### 一、主要参数说明：
+ src_folder_path：源文本的文件夹路径
+ dest_folder_path： 保存生成文件的文件夹路径
+ min_len：最小的文本长度，小于该长度将被丢弃。

##### 1. `__init__(self) `函数：
###### 功能：
+ 将模型`bert_model`由`MainModel`导入

##### 2. `sentiment_proportion(self,src_path,dest_path='情绪预测结果',min_len=1)`函数：
###### 主要参数：
+ `pro_dict`：情绪预测及占比结果

###### 功能：
+ 输出：
  从`src_path`引入数据使用函数`myClassification.get_predict_result`进行预测，再使用`calculate_label_proportions`计算占比，输出到`dest_path`位置

##### 3. `sentiment_ratio_pie(self,src_path,folder_path='情绪占比饼状图',min_len=1)`函数：
###### 功能：
+ 输出：
  将`src_path`路径文件由`draw_pie`函数转换成饼状图保存

##### 4. `risk_rank(self,src_path,min_len=1)`函数：
###### 功能：
+ 输出：
  将`src_path`的文本文件转换为风险等级

##### 5. `risk_rank_plot(self,src_folder_path,dest_folder_path='风险等级折线图',min_len=1)`函数：
###### 功能：
+ 输出：
  将`src_folder_path`转换为风险等级折线图

##### 6. `risk_rank_list(self,src_folder_path,min_len=1)`函数：
###### 主要参数：
+ `res_rank_list=[]`：记录风险等级的列表

###### 功能：
+ 输出：
  将`src_folder_path`路径下的文件转换成风险等级列表

##### 7. `emotions_proportion(self,src_path,min_len=1)`函数：
###### 功能：
+ 输出：
  将`src_path`转换成情绪预测的键值对

##### 8. `batch_sentiment_proportion(self,src_folder_path,dest_folder_path="情绪预测结果",min_len=1)`函数：
###### 功能：
+ 输出：
  从`src_folder_path`导入数据后输出情绪预测结果

##### 9. `batch_risk_rank_plot(self,src_folder_path,dest_folder_path='风险等级折线图',min_len=1)`函数：
###### 功能：
+ 输出：
  由用户文件绘制折线图

##### 10. `batch_sentiment_ratio_pie(self,src_folder_path,dest_folder_path='情绪占比饼状图',min_len=1)`函数：
###### 功能：
+ 输出：
  由用户文件绘制饼状图

### helper.ipynb

用于计算各项阈值，只需运行一次得到所有阈值。



# 