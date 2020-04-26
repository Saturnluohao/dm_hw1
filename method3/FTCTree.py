import math

import numpy as np


class FTCTree:
    def __init__(self, vipno=''):
        self.stat = {
            'nodeNum': 0,
            'freqSum': 0,
            'maxFreq': 0
        }
        self.vipno = vipno
        self.tree = {}
        self.freq = 0

    def add_freq(self, num):
        self.freq += num

    def set(self, key, num=1):
        """
        为树添加新的种类，同时设置频次
        :param key:
        :param num:
        :return:
        """
        keys = self.tree.keys()
        if key not in keys:
            self.tree[key] = FTCTree(self.vipno)
        self.tree[key].add_freq(num)

    def get_subtree(self, key):
        """
        根据种类名返回相应的子树
        :param key:
        :return: FTCTree
        """
        if key not in self.tree.keys():
            raise KeyError("No such key exists!")
        return self.tree[key]

    def get_freq(self, key):
        """
        获取本树某种类的购买频次
        :param key: 种类名
        :return:
        """
        if key not in self.tree.keys():
            raise KeyError("No such key exists!")
        return self.tree[key].freq

    def del_key(self, key):
        """
        删除名为key的种类
        :param key: 种类名
        :return:
        """
        del self.tree[key]

    def keys(self):
        """
        返回本树存储的种类集合
        :return: dict
        """
        return self.tree.keys()

    def empty(self):
        """
        判断是否是空树
        :return: bool
        """
        return True if len(self.tree) == 0 else False

    def mutable_keys(self):
        """
        返回本树存储的种类集合的可修改副本
        :return:
        """
        key_list = list(self.tree.keys())
        return {}.fromkeys(key_list, [])

    def update_node_num(self, stat):
        """
        递归更新树的节点数
        :return:
        """
        for key in self.keys():
            stat['nodeNum'] += 1
            self.get_subtree(key).update_node_num(stat)

    def mean_freq(self):
        self.stat['nodeNum'] = 0
        self.stat['freqSum'] = 0
        self.update_node_num(self.stat)

        for key in self.keys():
            self.stat['freqSum'] += self.get_freq(key)
        mean_freq = self.stat['freqSum'] / self.stat['nodeNum']

        print("The mean freq of the cluster {} is {}, total node amount is {}".
              format(self.vipno, mean_freq, self.stat['nodeNum']))

        return mean_freq

    def update_max_freq(self, stat):
        for key in self.keys():
            curFreq = self.get_freq(key)
            if curFreq > stat['maxFreq']:
                stat['maxFreq'] = curFreq
            self.get_subtree(key).update_max_freq(stat)

    def max_freq(self):
        self.stat['maxFreq'] = 0
        self.update_max_freq(self.stat)
        print("The max freq of cluster {} is {}".format(self.vipno, self.stat['maxFreq']))
        return self.stat['maxFreq']

    def __sub__(self, other):
        """
        两树之差为两树之间的距离
        :param other: 另一棵树
        :return: 两树间距离
        """
        return get_dis(self, other)

    def clone(self):
        ftctree = FTCTree()
        ftctree.tree = self.tree.copy()
        ftctree.freq = self.freq
        ftctree.vipno = self.vipno
        for key in self.tree.keys():
            ftctree.tree[key] = self.tree[key].clone()
        return ftctree

    def __eq__(self, other):
        if not self.keys() == other.keys():
            return False
        for key in self.keys():
            if not self.get_subtree(key) == other.get_subtree(key):
                return False
        return True


# 空树对象
EMPTY_TREE = FTCTree()


def get_dis(ftctree1, ftctree2):
    """
    获取两棵树之间的距离
    :param ftctree1: 树1
    :param ftctree2: 树2
    :param level: 树最高层级数
    :return: 两树之间的距离
    """

    inters_tree = get_inters(ftctree1, ftctree2)  # 构造交集树
    union_tree = get_union(ftctree1, ftctree2)  # 构造并集树
    sim_dict = {}
    sim_sum = 0

    # 交集为空则返回1
    if inters_tree.empty():
        return 1

    calculate_dis(inters_tree, union_tree, sim_dict, 1)  # 计算每个层级的相似系数
    level_sum = np.array(range(max(sim_dict.keys()) + 1)).sum()  # 计算层级数总和
    # level_sum = np.array(range(5)).sum()  # 计算层级数总和

    for level in sim_dict.keys():  # 将各层级的相似度乘以对应的权重求和
        w = level / level_sum
        sim_sum += (sim_dict[level] * w)

    sim_sum = 1 - sim_sum
    if sim_sum < 0:
        sim_sum = 0
    return sim_sum


def calculate_dis(inters_tree, union_tree, sim_dict, level):
    """
    获取两棵FTCTree之间的距离
    :param ftctree1: 参与距离计算的树
    :param ftctree2: 参与距离运算的树
    :return:
    """
    if inters_tree.empty() or level <= 0:
        return

    inters_keys = inters_tree.keys()
    union_keys = union_tree.keys()

    sims = []
    union_freq_sum = get_freq_sum_by_level(union_tree)
    if union_freq_sum == 0:
        print("Hello World")
    for key in inters_keys:
        if key in union_keys:
            sims.append(inters_tree.get_freq(key) / union_freq_sum)
            calculate_dis(inters_tree.get_subtree(key), union_tree.get_subtree(key), sim_dict, level + 1)
    # sim = np.array(sims).mean()
    sim = np.array(sims).sum()
    sim_dict[level] = sim


def get_freq_sum_by_level(ftctree):
    """
    获取TTCTree上某一层级所有种类的频次和
    :param ftctree: 树
    :return: int
    """
    freq = 0
    for key in ftctree.keys():
        freq += ftctree.get_freq(key)
    return freq


def get_inters(ftctree1, ftctree2):
    """
    获取FTCTree的交集树
    :param ftctree1: 参与交集运算的树
    :param ftctree2: 参与交集运算的树
    :return:
    """
    ftctree = FTCTree()
    construct_inters(ftctree1, ftctree2, ftctree)
    return ftctree


def get_union(ftctree1, ftctree2):
    """
    获取FTCTree的并集
    :param ftctree1: 参与并集运算的树
    :param ftctree2: 参与并集运算的树
    :return:
    """
    ftctree = FTCTree()
    construct_union(ftctree1, ftctree2, ftctree)
    return ftctree


def construct_inters(ftctree1, ftctree2, ftctree):
    """
    构造FTCTree的交集树
    :param FTCTree ftctree1: 参与交集运算的树
    :param FTCTree ftctree2: 参与交集运算的树
    :param FTCTree ftctree: 存放交集结果的树
    :return:
    """

    if ftctree1.empty() or ftctree2.empty():
        return

    keys1 = ftctree1.keys()
    keys2 = ftctree2.keys()

    for key in keys1:
        if key in keys2:
            ftctree.set(key, ftctree1.get_freq(key) + ftctree2.get_freq(key))
            construct_inters(ftctree1.get_subtree(key), ftctree2.get_subtree(key), ftctree.get_subtree(key))


def construct_union(ftctree1, ftctree2, ftctree):
    """
    构造FTCTree的并集
    :param FTCTree ftctree1: 参与并集运算的树
    :param FTCTree ftctree2: 参与并集运算的树
    :param FTCTree ftctree: 存放并集结果的树
    :return:
    """

    if ftctree1.empty() and ftctree2.empty():
        return

    keys1 = ftctree1.mutable_keys()
    keys2 = ftctree2.keys()

    for key in keys2:
        if key in keys1:
            ftctree.set(key, ftctree1.get_freq(key) + ftctree2.get_freq(key))
            construct_union(ftctree1.get_subtree(key), ftctree2.get_subtree(key), ftctree.get_subtree(key))
            del keys1[key]

        else:
            ftctree.set(key, ftctree2.get_freq(key))
            construct_union(ftctree2.get_subtree(key), EMPTY_TREE, ftctree.get_subtree(key))

    for key in keys1.keys():
        ftctree.set(key, ftctree1.get_freq(key))
        construct_union(ftctree1.get_subtree(key), EMPTY_TREE, ftctree.get_subtree(key))


def get_cluster_center(tree_cluster):
    """
    获取FTCTree簇的中心
    :param tree_cluster: 树簇
    :return: 树簇的中心
    """
    utree = union_tree_of_cluster(tree_cluster)
    ct = FTCTree()

    freq = 1
    mindist = np.Inf
    freqStep = utree.mean_freq()
    freqEnd = utree.max_freq()

    unchanged_time = 0
    last_dist = 0

    while freq <= freqEnd:
        if unchanged_time > 5:
            break

        utree = update_tree(utree, freq)
        dist = dis_sum(tree_cluster, utree)
        if math.fabs(last_dist - dist) < 0.1:
            unchanged_time += 1

        last_dist = dist

        # print("freq is {}, dist is {}".format(freq, dist))
        if dist < mindist:
            mindist = dist
            ct = utree.clone()
        freq += freqStep
    return ct


def update_tree(utree, freq):
    """
    删除频次低于freq的节点
   :param utree: FTCTree
    :param freq:
    :return: 更新之后的树
    """
    for key in utree.mutable_keys():
        update_tree(utree.get_subtree(key), freq)
        if utree.get_freq(key) < freq:
            utree.del_key(key)
            # print("delete node key {} in cluster {}".format(key, utree.vipno))

    return utree


def dis_sum(tree_cluster, center_tree):
    """
    计算簇中所有树到中心树的距离之和
    :param tree_cluster: 簇
    :param center_tree: 中心
    :return: 簇中所有树到中心的距离之和
    """
    sum = 0
    for tree in tree_cluster:
        sum += get_dis(tree, center_tree)
    return sum


def union_tree_of_cluster(tree_cluster):
    union_tree = FTCTree()
    for tree in tree_cluster:
        union_tree = get_union(union_tree, tree)
    return union_tree
