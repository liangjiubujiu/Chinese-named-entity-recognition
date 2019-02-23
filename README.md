# Undergraduate_Thesis-Chinese_Named_Entity_Recognition
My undergraduate thesis is Chinese named entity recognition based on bi-RNN(LSTM), this paper won the excellent thesis (top 1%) at July,2018.

命名实体识别输入一个 句子输出句子中实体类别及其位置。该模型中可识别的实体分为人名、地名和机构名。
中文和英文实体识别任务的不同之处在于英文是以单个字为一个单元，而中文是以多个字组成的词汇为一个单元。中文命名实体识别要求对句子中词汇切分，并识别出实体的位置和边界。

使用CPU版本的TensorFlow的框架搭建了Bi-LSTM+条件随机场模型,输入三个句子，判断结果看到，准确地完成了中文命名实体识别地任务,网络结构如下：中文分词（结巴）、词嵌入（word embedding）、一层双向LSTM、条件随机场和维特比解码算法。

<img src="https://github.com/liangjiubujiu/Undergraduate_Thesis-Chinese_Named_Entity_Recognition/blob/master/images/3.jpg" height="400" width="400" />

## 第一个实验 Evaluation of varied news corpus
这是对不同内容主题的新闻语料进行测试，测试数据涵盖教育、法律、政治天气等多个方面的内容。从以下汇总的实验结果来看，准确率、精确率和召回率均达到较高水平，即90%以上。F1指标相较于主流的英文命名实体模型，略逊色一分。在中文分词阶段会引入误差，加大中文命名实体识别难度，这一原因了导致的F1指标下降。

<img src="https://github.com/liangjiubujiu/Undergraduate_Thesis-Chinese_Named_Entity_Recognition/blob/master/images/1.jpg" height="400" width="800" />

### 第二个实验 Personal names with uncommon characters
含生僻字的中文名字：田堃 孟美岐；英文名字：姜丹尼尔；韩文名字 ：朴有天；最新的名人姓名：何炅。
测试结果是有两个名字(蓝框和绿框)没有被正确识别,原因是这两个名字里的人名字中的字在地名和机构名也过于常见，判别为其他实体的概率也很大.

<img src="https://github.com/liangjiubujiu/Undergraduate_Thesis-Chinese_Named_Entity_Recognition/blob/master/images/2.jpg" height="300" width="600" />

