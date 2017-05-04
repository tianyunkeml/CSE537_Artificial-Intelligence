import pandas as pd
import sys
import xlwt
import time
import scipy.stats as ss
import math

class_name = 'Type de roche'
CONFIDENCE = 0.975
MY_BINS = 3
FILENAME = 'bakarydata3.xls'
MAX = 350000

def data_clean(ini_list,confid):
	list1 = ini_list
	mean = (sum(list1)) / len(list1)
	temp3 = 0
	outlier = []
	for i in list1:
		temp1 = (i - mean)
		temp2 = temp1 ** 2
		temp3 += temp2
	var = float(temp3) / ((len(list1) - 1) + 0.000000000001)
	for i in list1:
		temp1 = abs(i - mean)
		temp2 = (var) ** 0.5
		p = temp1 / temp2
		if p > ss.norm.ppf(CONFIDENCE):
			outlier.append(i)
	for i in outlier:
		list1.remove(i)
	new_mean = (sum(list1)) / len(list1)
	return [new_mean,outlier]

def dataCollect(myFile,attr):
	ind = myFile.index
	c_label = []
	dataDict = {}
	for my_ind in ind:
		if myFile.loc[my_ind,class_name] not in c_label:
			c_label.append(myFile.loc[my_ind,class_name])
	for c_name in c_label:
		dataDict[c_name] = []
	for my_ind in ind:
		tmp = myFile.loc[my_ind,attr]
		if isinstance(tmp,float):
			if math.isnan(tmp) == True:
				continue
		if isinstance(tmp,str) or isinstance(tmp,int):
			tmp = float(tmp)
		dataDict[myFile.loc[my_ind,class_name]].append(tmp)
	return dataDict

def discrete1(mylist,bins):
	mylist.sort()
	n = int(len(mylist) / bins)
	res = []
	for i in range(bins):
		if i == bins - 1:
			low = mylist[i * n]
			up = mylist[len(mylist) - 1]
		else:
			low = mylist[i * n]
			up = mylist[i * n + n]
		repre = (low + up) / 2
		res.append((low,up,repre))
	return res

def discrete2(mylist):
	my_max = max(mylist)
	my_min = min(mylist)
	dif = float(my_max - my_min)
	div = 0.00001
	m = dif / div
	res = []
	while m > 10:
		div *= 10
		m = dif / div
	m = int(m)
	if m in [3,6,7,9]:
		k = 3
	elif m in [2,4,8]:
		k = 4
	else:
		k = 5
	step = dif / k
	for i in range(k):
		res.append((my_min + i * step,my_min + (i + 1) * step,my_min + (i + 0.5) * step))
	return res

def discretize(model,num):
	for interval in model:
		if num >= interval[0] and num <= interval[1]:
			return interval[2]

def get_my_df(myFile,discrete = True,dis_method = 1):
	col = myFile.columns
	ind = myFile.index
	attr_set = col.drop(class_name)
	drop_list = []
	for attr in attr_set:
		dataDict = dataCollect(myFile,attr)
		for c_label,my_list in dataDict.items():
			if len(my_list) == 0:
				drop_list.append(attr)
				break
			new_mean,outlier = data_clean(my_list,CONFIDENCE)
			new_list = []
			for my_ind in ind:
				if myFile.loc[my_ind,class_name] == c_label:
					if myFile.loc[my_ind,attr] in outlier or math.isnan(myFile.loc[my_ind,attr]):
						myFile.loc[my_ind,attr] = new_mean
					new_list.append(myFile.loc[my_ind,attr])
			if discrete:
				if dis_method == 1:
					dis_model = discrete1(new_list,MY_BINS)
				if dis_method == 2:
					dis_model = discrete2(new_list)
				for my_ind in ind:
					if myFile.loc[my_ind,class_name] == c_label:
						myFile.loc[my_ind,attr] = discretize(dis_model,myFile.loc[my_ind,attr])
	mycol = col
	for d_attr in drop_list:
		mycol = mycol.drop(d_attr)
	myFile = myFile[mycol]
	col = myFile.columns.drop(class_name)
	ind = myFile.index
	for my_ind in ind:
		for my_col in col:
			myFile.loc[my_ind,my_col] = float(myFile.loc[my_ind,my_col]) / MAX
	return myFile

def my_main(fn):
	myFile = pd.read_excel(fn)
	#newFile = get_my_df(myFile,True,1)
	#newFile = get_my_df(myFile,True,2)
	newFile = get_my_df(myFile,discrete = False)
	newFile.to_csv('./Preprocessed.csv')

if __name__ == '__main__':
	my_main(FILENAME)


