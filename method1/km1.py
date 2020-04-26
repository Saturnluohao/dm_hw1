import pandas as pd
from util.DataItem import DataItem
from util.center_initializer import kmeans_plusplus_initializer
from util.my_kmeans import my_kmeans
from util.my_metric import my_metric
import numpy as np

data = pd.read_csv("data/trade_new.csv", converters={'vipno': str, 'pluno': str}, usecols=['vipno', 'pluno', 'amt'], index_col=False)
data['pluno'] = data['pluno'].map(lambda x: x[0 : 5])
items = []
print(len(data.groupby('vipno').groups))
for vipno, group in data.groupby('vipno'):
    bought_list = group.groupby('pluno')['amt'].sum()
    dataItem = DataItem(vipno, [bought_list.to_dict()])
    items.append(dataItem)
items = np.array(items)

def data_item_metric(dataItem1, dataItem2):
    return dataItem1 - dataItem2

sc = open('sc.txt', mode='a')
cp = open('cp.txt', mode='a')

for i in range(25,26):
    initial = kmeans_plusplus_initializer(items, i, kmeans_plusplus_initializer.FARTHEST_CENTER_CANDIDATE).initialize()

    my_kmeans_instance = my_kmeans(items, initial, 50, data_item_metric)
    my_kmeans_instance.process()
    my_metric_instance = my_metric(items, my_kmeans_instance.get_clusters(), my_kmeans_instance.get_centers())

    print("k is {}".format(i))
    print("sc is {}".format(my_metric_instance.get_sc()))
    print("cp is {}".format(my_metric_instance.get_cp()))

    # sc.write("{},".format(i))
    # cp.write('{},'.format(i))
    # sc.write("{}\n".format(my_metric_instance.get_sc()))
    # cp.write("{}\n".format(my_metric_instance.get_cp()))

sc.close()
cp.close()
