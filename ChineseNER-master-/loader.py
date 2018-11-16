import os
import re
import codecs

from data_utils import create_dico, create_mapping, zero_digits
from data_utils import iob2, iob_iobes, get_seg_features


def load_sentences(path, lower, zeros):
    """
    Load sentences. A line must contain at least a word and its tag.
    Sentences are separated by empty lines.
    """
    sentences = []
    sentence = []
    num = 0
    for line in codecs.open(path, 'r', 'utf8'):
        num+=1
        line = zero_digits(line.rstrip()) if zeros else line.rstrip()
        # 即根据zeros的真假确定line的赋值，True则赋值为：zero_digits(line.rstrip())， 反之则赋值为line.rstrip()
        # str.rstrip([chars]); chars -- 指定删除的字符（默认为空格）; 返回删除 string 字符串末尾的指定字符后生成的新字符串。
        # 而对于txt中的“\n”而言，对它进行rstrip操作会把它变成[], 从而方便把句子区分开
        if not line:
        # 空列表相当于 False
            if len(sentence) > 0:
                if 'DOCSTART' not in sentence[0][0]:
                    sentences.append(sentence)
                    # append() 方法用于在列表末尾添加新的对象。
                sentence = []
                # 这里的操作是利用回车给句子分段，并分别将每个句子存在sentences里
        else:
            if line[0] == " ":
                line = "$" + line[1:]
                word = line.split()
                # 感觉这里是把空格行用“$”标注的样子
            else:
                word= line.split()
                # str.split(str="", num=string.count(str))
                # 通过指定分隔符对字符串进行切片，如果参数num 有指定值，则仅分隔 num 个子字符串
                # str -- 分隔符，默认为所有的空字符，包括空格、换行(\n)、制表符(\t)等； num -- 分割次数。
                # 这里会将'海 0\n'分成['海'，'0']
            assert len(word) >= 2, print([word[0]])
                # 不满足assert条件报错
                # 如果word的长度小于2 则会打印word首字然后报Assertion的错 即认为一个词对应一个标签
            sentence.append(word)
                # sentence 存储的是每个词签对的列表
    # 这个循环操作是把文档逐字地进行读取，并读取每个字的标签
    if len(sentence) > 0:
        if 'DOCSTART' not in sentence[0][0]:
            sentences.append(sentence)
    return sentences


def update_tag_scheme(sentences, tag_scheme):
    """
    Check and update sentences tagging scheme to IOB2.
    Only IOB1 and IOB2 schemes are accepted.
    """
    
    # enumerate() 函数用于将一个可遍历的数据对象组合为一个索引序列，同时列出数据和数据下标，一般用在 for 循环当中。
    # 这里i为从0开始的序列，i为每个句子的序号
    
    for i, s in enumerate(sentences):
        tags = [w[-1] for w in s]
        # 这里 tags 是取sentences中每个字的标签-- w[-1]的意思是取数组最后一位，并将标签按句子排成一个列表
        
        # Check that tags are given in the IOB format
        if not iob2(tags):
            s_str = '\n'.join(' '.join(w) for w in s)
            # join() 方法用于将序列中的元素以指定的字符<这里为‘ ’和‘\n’>连接生成一个新的字符串。
            # 以上将在错误信息中打印
            
            raise Exception('Sentences should be given in IOB format! ' +
                            'Please check sentence %i:\n%s' % (i, s_str))
        if tag_scheme == 'iob':
            # If format was IOB1, we convert to IOB2
            for word, new_tag in zip(s, tags):
                word[-1] = new_tag
        elif tag_scheme == 'iobes':
            new_tags = iob_iobes(tags) # iob_iobes是根据iob标签形成iobes
            for word, new_tag in zip(s, new_tags):
                word[-1] = new_tag     # 将原标签word[-1]换成新标签
        else:
            raise Exception('Unknown tagging scheme!')


def char_mapping(sentences, lower):  
    """
    Create a dictionary and a mapping of words, sorted by frequency.
    lower的预定值是：True
    """
    chars = [[x[0].lower() if lower else x[0] for x in s] for s in sentences]
    # Python lower() 方法转换字符串中所有大写字符为小写。
    # chars 存储的是语料里的每个字
    dico = create_dico(chars) # dico 为统计了语料中每个字出现的次数的字典
    dico["<PAD>"] = 10000001
    dico['<UNK>'] = 10000000
    char_to_id, id_to_char = create_mapping(dico)
    # 以上两个字典为对字频做了统计之后的字和id的互译字典，字频越大id越小
    print("Found %i unique words (%i in total)" % (
        len(dico), sum(len(x) for x in chars)
    ))
    return dico, char_to_id, id_to_char


def tag_mapping(sentences):
    """
    Create a dictionary and a mapping of tags, sorted by frequency.
    """
    tags = [[char[-1] for char in s] for s in sentences]
    dico = create_dico(tags)
    tag_to_id, id_to_tag = create_mapping(dico)
    print("Found %i unique named entity tags" % len(dico))
    return dico, tag_to_id, id_to_tag


def prepare_dataset(sentences, char_to_id, tag_to_id, lower=False, train=True):
    """
    Prepare the dataset. Return a list of lists of dictionaries containing:
        - word indexes
        - word char indexes
        - tag indexes
    """

    none_index = tag_to_id["O"]

    def f(x):
        return x.lower() if lower else x
    data = []
    for s in sentences:
        string = [w[0] for w in s]
        chars = [char_to_id[f(w) if f(w) in char_to_id else '<UNK>']
                 for w in string]
        segs = get_seg_features("".join(string))
        
        '''
            string 储存的是每个句子里的字 
            chars  储存的是每个句子里的字对应的id，如果字典中不存在这个字，则返回<'UNK'>(感觉是Unkown的意思)对应的id
            segs   存储的是用jieba分词分词后，用基于词长度划分的特征的组合，例如[1,3,|0,|0,|1,2,2,3]：
                   词长   特征（feature）
                    1    [0]
                    2    [1,3]
                    3    [1,2,3]
                    4    [1,2,2,3]
                    5    [1,2,2,2,3]
                   ...   ...
                   注："char".join([strlist]), 意识是将一个字符list中的元素用""中对应的字符连接，这里为空，所以直接连接
        '''
        
        if train:
            tags = [tag_to_id[w[-1]] for w in s]
        else:
            tags = [none_index for _ in chars]
        data.append([string, chars, segs, tags])
        # data 以句子为单位存储[字符，字符id，标签id/chars长度的全是“0”对应标签id的list，标签]

    return data


def augment_with_pretrained(dictionary, ext_emb_path, chars):
    """
    Augment（扩充） the dictionary with words that have a pretrained embedding.
    If `words` is None, we add every word that has a pretrained embedding
    to the dictionary, otherwise, we only add the words that are given by
    `words` (typically the words in the development and test sets.)
    
    上文中的‘words’就是这里传入的chars
    """
    # 由上述注释所示：传入的chars是test语料集的字集list
    # 即将要把wiki_100中能查寻到的test语料集中的字加到训练字典中
    
    print('Loading pretrained embeddings from %s...' % ext_emb_path)
    assert os.path.isfile(ext_emb_path)
    
    # 这里用的wiki_100.utf8 为字符的向量字典

    # Load pretrained embeddings from file
    pretrained = set([
        line.rstrip().split()[0].strip()
        for line in codecs.open(ext_emb_path, 'r', 'utf-8')
        if len(ext_emb_path) > 0
    ])
    
    # set() 函数创建一个无序不重复元素集，可进行关系测试，删除重复数据，还可以计算交集、差集、并集等。
    # rstrip() 删除 string 字符串末尾的指定字符（默认为空格）
    # strip() 方法用于移除字符串头尾指定的字符（默认为空格）
    # 所以这里pretrained得到的是wiki_100里的字符集

    # We either add every word in the pretrained file,
    # or only words given in the `words` list to which
    # we can assign a pretrained embedding
    if chars is None:
        for char in pretrained:
            if char not in dictionary:
                dictionary[char] = 0
    else:
        for char in chars:
            if any(x in pretrained for x in [
                char,
                char.lower(),
                re.sub('\d', '0', char.lower())
            ]) and char not in dictionary:
            # any() 函数用于判断给定的可迭代参数 iterable 是否全部为空对象，如果都为空、0、false，则返回 False，
            #       如果不都为空、0、false，则返回 True。
            
            # Python 的re模块提供了re.sub用于替换字符串中的匹配项。这里‘\d’表示任意数字，意思是把所有数字替换成‘0’
            
            # x in [list1] for x in [list2]: 是指对list2中的元素，判断其在不在list1中
            # eg   >> p = ['1','2','3','4','5']；l = ['2','6']
            #      >> list（x in l for x in p）
            #      >> out: [False,True,False,False,False]
            # any是用来判断这个列表里是不是都是False的
            
                dictionary[char] = 0
            '''
                上面的if语句是判断chars中的字符是否存在于wiki_100中并且是否不存在于之前的train集字典中
            '''
    word_to_id, id_to_word = create_mapping(dictionary)  # 这一步就是把list转换成字典
    return dictionary, word_to_id, id_to_word


def save_maps(save_path, *params):
    """
    Save mappings and invert mappings
    """
    pass
    # with codecs.open(save_path, "w", encoding="utf8") as f:
    #     pickle.dump(params, f)


def load_maps(save_path):
    """
    Load mappings from the file
    """
    pass
    # with codecs.open(save_path, "r", encoding="utf8") as f:
    #     pickle.load(save_path, f)

