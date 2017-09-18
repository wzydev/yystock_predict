#!/usr/bin/python
#coding:utf-8
'''
数据相关处理函数
'''
import pdb
import copy
import numpy as np

from pymongo import MongoClient

def gen_train_data(coll,scode,ts_from=None):
    lst = []
    yesterday_close = None
    cursor = coll.find({"scode":scode}).sort("rdate")
    for item in cursor:
        if yesterday_close == None:
            yesterday_close = item["p_open"]
        change = (item["p_close"] - yesterday_close)/yesterday_close
        label = 0
        lst.append([item["p_open"],item["p_close"],item["p_low"],item["p_high"],item["volumn"],item["money"],change,label])
        yesterday_close = item["p_close"]
    return lst

def fill_label_tmw_low(lst_raw,rm_last=True):
    lst = copy.deepcopy(lst_raw)
    for i in range(len(lst)-1):
        lst[i][-1] = lst[i+1][2]  #标签设为明天的最低价
    return lst[:-1]

def fill_label_day_after_tmw_high(lst_raw,rm_last=True):
    lst = copy.deepcopy(lst_raw)
    for i in range(len(lst)-2):
        lst[i][-1] = lst[i+2][3]  #标签设为后天的最高价
    return lst[:-2]


def get_train_data_tmw_low(coll,scode,batch_size=60,time_step=20):
    batch_index=[]
    data_raw=gen_train_data(coll,scode)
    data_fill = fill_label_tmw_low(data_raw)
    data_train = np.array(data_fill)
    normalized_train_data=(data_train-np.mean(data_train,axis=0))/np.std(data_train,axis=0)  #±ê×¼»¯
    train_x,train_y=[],[]
    for i in range(len(normalized_train_data)-time_step):
       if i % batch_size==0:
           batch_index.append(i)
       x=normalized_train_data[i:i+time_step,:7]
       y=normalized_train_data[i:i+time_step,7,np.newaxis]
       train_x.append(x.tolist())
       train_y.append(y.tolist())
    batch_index.append((len(normalized_train_data)-time_step))
    return batch_index,train_x,train_y

def get_train_data_day_after_tmw_high(coll,scode,batch_size=60,time_step=20):
    batch_index=[]
    data_raw=gen_train_data(coll,scode)
    data_fill = fill_label_day_after_tmw_high(data_raw)
    data_train = np.array(data_fill)
    normalized_train_data=(data_train-np.mean(data_train,axis=0))/np.std(data_train,axis=0)  #±ê×¼»¯
    train_x,train_y=[],[]
    for i in range(len(normalized_train_data)-time_step):
       if i % batch_size==0:
           batch_index.append(i)
       x=normalized_train_data[i:i+time_step,:7]
       y=normalized_train_data[i:i+time_step,7,np.newaxis]
       train_x.append(x.tolist())
       train_y.append(y.tolist())
    batch_index.append((len(normalized_train_data)-time_step))
    return batch_index,train_x,train_y

def get_test_data(coll,scode,time_step=20):
    data_raw = get_train_data(coll,scode)
    data_test = np.array(data_raw[-20:])
    mean=np.mean(data_test,axis=0)
    std=np.std(data_test,axis=0)
    normalized_test_data=(data_test-mean)/std
    size=(len(normalized_test_data)+time_step-1)//time_step
    test_x,test_y=[],[]  
    for i in range(size-1):
       x=normalized_test_data[i*time_step:(i+1)*time_step,:7]
       y=normalized_test_data[i*time_step:(i+1)*time_step,7]
       test_x.append(x.tolist())
       test_y.extend(y)
    test_x.append((normalized_test_data[(i+1)*time_step:,:7]).tolist())
    test_y.extend((normalized_test_data[(i+1)*time_step:,7]).tolist())
    return mean,std,test_x,test_y


if __name__ == "__main__":
    client = MongoClient("s.izhiyi.pub",11281)
    coll = client["test"]["stock_history"]
    data = gen_train_data(coll,"600452")
    pdb.set_trace()
    data1 = fill_label_tmw_low(data)
    data2 = fill_label_day_after_tmw_high(data)
    pdb.set_trace()
