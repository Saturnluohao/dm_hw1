# --coding:utf-8--
import datetime
from math import log

from sklearn.metrics import silhouette_score

import method3.FTCTree as ftct
from method3.FTCTree import FTCTree
import pandas as pd
from util.my_kmeans import my_kmeans
import numpy as np
from util.center_initializer import kmeans_plusplus_initializer


# 针对FTCTree簇的中心计算方式重写kmeans计算簇中心的方法
from util.my_metric import my_metric_for_ftctree
import matplotlib.pyplot as plt

class my_kmeans_for_FTCTree(my_kmeans):
    def __init__(self, data, initial_centers, itermax, metric, tolerance=0.001):
        my_kmeans.__init__(self, data, initial_centers, itermax, metric, tolerance)

    def update_centers(self):
        centers = []

        for index in range(len(self._clusters)):
            cluster_points = self._pointer_data[self._clusters[index]]
            newCenter = ftct.get_cluster_center(cluster_points)
            centers.append(newCenter)
        return centers


def ftctree_metric(ftctree1, ftctree2):
    if isinstance(ftctree1, list) and isinstance(ftctree2, list):
        if len(ftctree1) != len(ftctree2):
            return
        ans = []
        for i in range(len(ftctree1)):
            ans.append(ftctree1[i] - ftctree2[i])
        return ans

    return ftctree1 - ftctree2


BASE_DATE = datetime.datetime.strptime('2016-08-01 00:00:00', "%Y-%m-%d %H:%M:%S")
data = pd.read_csv("../data/trade_new.csv",
                   converters={'vipno': str, 'pluno': str},
                   usecols=['sldatime', 'vipno', 'pluno'],
                   index_col=False)
data['sldatime'].map(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))

groups_by_vipno = data.groupby('vipno')

ftctrees = []

for vipno, group in groups_by_vipno:
    ftctree = FTCTree(vipno)
    for i, row in group.iterrows():
        date = datetime.datetime.strptime(row['sldatime'], "%Y-%m-%d %H:%M:%S")
        days = (BASE_DATE - date).days
        ori_pluno = row['pluno']
        decayed_pluno = ''
        if days <= 30:
            decayed_pluno = ori_pluno[0: 5]
        elif 30 < days <= 60:
            decayed_pluno = ori_pluno[0: 4]
        elif 60 < days < 120:
            decayed_pluno = ori_pluno[0: 3]
        else:
            decayed_pluno = ori_pluno[0: 2]

        category = decayed_pluno[0: 2]
        ftctree.set(category)
        index = 2
        tempTree = ftctree.get_subtree(category)
        ''':type: FTCTree'''

        while index < len(decayed_pluno):
            key = decayed_pluno[index]
            index += 1
            tempTree.set(key)
            tempTree = tempTree.get_subtree(key)
    ftctrees.append(ftctree)

ftctrees = np.array(ftctrees)

# length = len(ftctrees)
# dis_mat = np.zeros((length, length))
# label = [0] * length
# for i in range(length):
#     for j in range(i + 1):
#         dis_mat[j, i] = dis_mat[i, j] = ftctrees[i] - ftctrees[j]
#
# dis_per = []
# dis = ['0.2', '0.4', '0.6', '0.8', '1.0']
# for i in range(5):
#     dis_per.append(len(dis_mat[(dis_mat > i * 0.2) & (dis_mat < (i+1)*0.2)]))
# dis_per = np.array(dis_per)
# amount_sum = dis_per.sum()
# dis_per = dis_per / amount_sum
# plt.xlabel("Distance")
# plt.ylabel("Percentage")
# plt.bar(dis, dis_per)
# plt.show()


def run_two_means(ftctrees, max_iter):
    initial = kmeans_plusplus_initializer(ftctrees, 2,
                                          kmeans_plusplus_initializer.FARTHEST_CENTER_CANDIDATE).initialize()
    my_kmeans_instance = my_kmeans_for_FTCTree(ftctrees, initial, max_iter, ftctree_metric)
    my_kmeans_instance.process()
    return my_kmeans_instance


def count_category_num(ftctree, prefix, category_dict):
    """
    计算簇中商品的种类数
    :param FTCTree ftctree: 树
    :param str prefix: 种类前缀
    :param dict category_dict: 统计种类数的字典
    :return:
    """
    if ftctree.empty():
        category_dict[prefix] = 1
        return
    for key in ftctree.keys():
        count_category_num(ftctree.get_subtree(key), prefix + key, category_dict)


def get_cluster_categories(ftctrees, isCluster):
    category_dict = {}
    if isCluster:
        for cluster in ftctrees:
            for tree in cluster:
                count_category_num(tree, '', category_dict)
    else:
        for tree in ftctrees:
            count_category_num(tree, '', category_dict)

    return len(category_dict)


def bic_score(clusters, centers):
    global likelihood
    N = 0
    C = len(clusters)
    PI = 3.14
    bic = 0

    for cluster in clusters:
        N += len(cluster)

    for i in range(len(clusters)):
        cluster = clusters[i]
        center = centers[i]
        Ni = len(cluster)
        D = get_cluster_categories(cluster, False)
        dist_to_center_sum = 0

        for j in range(len(cluster)):
            dist = ftct.get_dis(cluster[j], center)
            dist_to_center_sum += (dist * dist)
        sigma_square = dist_to_center_sum * (Ni - C) / 2
        # sigma_square = dist_to_center_sum / Ni

        if Ni == 0 or N == 0 or sigma_square == 0 or C == 0:
            return -np.Inf

        try:
            likelihood = Ni * (log(Ni, 2) - log(N, 2) - log(2 * PI, 2) / 2 - D * log(sigma_square, 2) / 2) - (
                        Ni - C) / 2
        except ValueError:
            print("Value Error")
        bic += (likelihood - C * (D + 1) * log(C, 2) / 2)
    return bic


clusters = []
cluster_centers = []


def split(cluster, center):
    if len(cluster) <= 5:
        clusters.append(cluster)
        return
    my_kmeans_instance = run_two_means(cluster, 15)
    centers = my_kmeans_instance.get_centers()
    splited_clusters = my_kmeans_instance.get_clusters()
    if len(splited_clusters) == 1:
        clusters.append(cluster)
        return

    cluster1 = cluster[splited_clusters[0]]
    cluster2 = cluster[splited_clusters[1]]
    center1 = centers[0]
    center2 = centers[1]
    bic_before_split = bic_score([cluster], [center])
    bic_after_split = bic_score([cluster1, cluster2], [center1, center2])
    if bic_before_split < bic_after_split:
        split(cluster1, center1)
        split(cluster2, center2)
    else:
        clusters.append(cluster)
        cluster_centers.append(center)


split(ftctrees, ftct.get_cluster_center(ftctrees))

my_metric_instance = my_metric_for_ftctree(clusters, cluster_centers)

print("sc is {}".format(my_metric_instance.get_sc()))
print("cp is {}".format(my_metric_instance.get_cp()))
