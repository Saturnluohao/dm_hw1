import pandas as pd
from util.DataItem import DataItem
import numpy as np
from util.center_initializer import kmeans_plusplus_initializer
from util.my_kmeans import my_kmeans
from util.my_metric import my_metric

data = pd.read_csv("../data/trade_new.csv", converters={'vipno': str, 'pluno': str}, usecols=['vipno', 'pluno', 'amt'],
                   index_col=False)
data['pluno'] = data['pluno'].map(lambda x: x[0: 5])
dataItems = []
groups_by_vipno = data.groupby('vipno')

print(len(groups_by_vipno.groups))

for vipno, group in groups_by_vipno:
    bought_list_by_levels = []
    for i in range(4):
        group_cpy = group.copy(deep=True)
        ''':type: pd.DataFrame'''
        group_cpy['pluno'] = data['pluno'].map(lambda x: x[0:2 + i])
        bought_list = group_cpy.groupby('pluno')['amt'].sum()
        bought_list_by_levels.append(bought_list.to_dict())
    dataItem = DataItem(vipno, bought_list_by_levels)
    dataItems.append(dataItem)
items = np.array(dataItems)

print(dataItems[0] - dataItems[1])


def data_item_metric(dataItem1, dataItem2):
    return dataItem1 - dataItem2


sc = open('sc.txt', mode='a')
cp = open('cp.txt', mode='a')

for i in range(2, 100):
    initial = kmeans_plusplus_initializer(items, i, kmeans_plusplus_initializer.FARTHEST_CENTER_CANDIDATE).initialize()

    my_kmeans_instance = my_kmeans(items, initial, 50, data_item_metric)
    my_kmeans_instance.process()
    my_metric_instance = my_metric(items, my_kmeans_instance.get_clusters(), my_kmeans_instance.get_centers())

    print("k is {}".format(i))
    print("sc is {}".format(my_metric_instance.get_sc()))
    print("cp is {}".format(my_metric_instance.get_cp()))

    sc.write("{},".format(i))
    cp.write('{},'.format(i))
    sc.write("{}\n".format(my_metric_instance.get_sc()))
    cp.write("{}\n".format(my_metric_instance.get_cp()))

sc.close()
cp.close()
