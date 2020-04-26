from sklearn.metrics.cluster import silhouette_score
import numpy as np


class my_metric:
    def __init__(self, data, clusters, centers):
        '''
        :param [DataItem] data:
        :param [[int]] cluster:
        :param [DataItem] center:
        '''
        self.data = data
        self.clusters = clusters
        self.centers = centers

    def get_sc(self):
        label = [0] * len(self.data)
        for clusterID in range(len(self.clusters)):
            cluster = self.clusters[clusterID]
            for index in cluster:
                label[index] = clusterID
        length = len(self.data)
        dis_mat = np.zeros((length, length))
        for i in range(length):
            for j in range(i + 1):
                dis_mat[j, i] = dis_mat[i, j] = self.data[i] - self.data[j]
        return silhouette_score(dis_mat, label, metric='precomputed')

    def get_cp(self):
        cp = 0
        for i in range(len(self.clusters)):
            cluster = self.clusters[i]
            center = self.centers[i]
            cpi = 0
            for j in range(len(cluster)):
                cpi += (self.data[cluster[j]] - center)
            cp += (cpi / len(cluster))

        return cp / len(self.clusters)


class my_metric_for_ftctree:
    def __init__(self, clusters, centers):
        '''
        :param [DataItem] data:
        :param [[int]] cluster:
        :param [DataItem] center:
        '''
        self.data = np.concatenate(clusters)
        self.label = []
        for i in range(len(clusters)):
            cluster = clusters[i]
            for tree in cluster:
                self.label.append(i)
        self.clusters = clusters
        self.centers = centers

    def get_sc(self):
        length = len(self.data)
        dis_mat = np.zeros((length, length))
        for i in range(length):
            for j in range(i + 1):
                dis_mat[j, i] = dis_mat[i, j] = self.data[i] - self.data[j]
        return silhouette_score(dis_mat, self.label, metric='precomputed')

    def get_cp(self):
        cp = 0
        for i in range(len(self.clusters)):
            cluster = self.clusters[i]
            center = self.centers[i]
            cpi = 0
            for j in range(len(cluster)):
                cpi += (cluster[j] - center)
            cp += (cpi / len(cluster))

        return cp / len(self.clusters)
