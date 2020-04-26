import time

import numpy
from util.DataItem import DataItem

class my_kmeans:
    def __init__(self, data, initial_centers, itermax, metric, tolerance=0.001):
        self._pointer_data = data
        self._clusters = []
        self._centers = initial_centers
        self._tolerance = tolerance
        self._total_wce = 0.0
        self._metric = metric
        self._itermax = itermax
        self._verify_arguments()

    def process(self):
        maximum_change = float('inf')
        iteration = 0

        while maximum_change > self._tolerance and iteration < self._itermax:
            self._clusters = self.__update_clusters()
            updated_centers = self.update_centers()  # changes should be calculated before assignment
            maximum_change = self.__calculate_changes(updated_centers)

            print("iteration {}, the change is {}".format(iteration, maximum_change))
            for cluster in self._clusters:
                print(len(cluster))

            self._centers = updated_centers  # assign center after change calculation
            iteration += 1

        self.__calculate_total_wce()

    def predict(self, points):
        nppoints = numpy.array(points)
        if len(self._clusters) == 0:
            return []

        differences = numpy.zeros((len(nppoints), len(self._centers)))
        for index_point in range(len(nppoints)):
            differences[index_point] = [self._metric(nppoints[index_point], center) for center in self._centers]

        return numpy.argmin(differences, axis=1)

    def get_clusters(self):
        return self._clusters

    def get_centers(self):
        if isinstance(self._centers, list):
            return self._centers
        return self._centers.tolist()

    def get_total_wce(self):
        return self._total_wce

    def __update_clusters(self):
        clusters = [[] for _ in range(len(self._centers))]

        start = time.time()

        dataset_differences = self.__calculate_dataset_difference(len(clusters))

        print("Distance calculation costs {}".format(time.time() - start))

        optimum_indexes = numpy.argmin(dataset_differences, axis=0)
        for index_point in range(len(optimum_indexes)):
            index_cluster = optimum_indexes[index_point]
            clusters[index_cluster].append(index_point)

        clusters = [cluster for cluster in clusters if len(cluster) > 0]

        return clusters

    def update_centers(self):
        centers = []

        for index in range(len(self._clusters)):
            cluster_points = self._pointer_data[self._clusters[index]]
            newCenter = DataItem(index, [{}] * self.levels)
            for point in cluster_points:
                newCenter = point + newCenter
            newCenter / len(cluster_points)
            centers.append(newCenter)

        return numpy.array(centers)

    def __calculate_total_wce(self):
        dataset_differences = self.__calculate_dataset_difference(len(self._clusters))

        self._total_wce = 0
        for index_cluster in range(len(self._clusters)):
            for index_point in self._clusters[index_cluster]:
                self._total_wce += dataset_differences[index_cluster][index_point]

    def __calculate_dataset_difference(self, amount_clusters):
        dataset_differences = numpy.zeros((amount_clusters, len(self._pointer_data)))
        for index_center in range(amount_clusters):
            dataset_differences[index_center] = [self._metric(point, self._centers[index_center])
                                                 for point in self._pointer_data]

        return dataset_differences

    def __calculate_changes(self, updated_centers):
        if len(self._centers) != len(updated_centers):
            maximum_change = float('inf')

        else:
            changes = self._metric(self._centers, updated_centers)
            maximum_change = numpy.max(changes)

        return maximum_change

    def _verify_arguments(self):
        if len(self._pointer_data) == 0:
            raise ValueError("Input data is empty (size: '%d')." % len(self._pointer_data))
        if isinstance(self._pointer_data[0], DataItem):
            self.levels = len(self._pointer_data[0].bought_list_by_levels)

        if len(self._centers) == 0:
            raise ValueError("Initial centers are empty (size: '%d')." % len(self._pointer_data))

        if self._tolerance < 0:
            raise ValueError("Tolerance (current value: '%d') should be greater or equal to 0." %
                             self._tolerance)

        if self._itermax < 0:
            raise ValueError("Maximum iterations (current value: '%d') should be greater or equal to 0." %
                             self._tolerance)
