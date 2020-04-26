import numpy, random, warnings

class kmeans_plusplus_initializer:

    ## Constant denotes that only points with highest probabilities should be considered as centers.
    FARTHEST_CENTER_CANDIDATE = "farthest"

    def __init__(self, data, amount_centers, amount_candidates=None):
        """!
        @brief Creates K-Means++ center initializer instance.

        @param[in] data (array_like): List of points where each point is represented by list of coordinates.
        @param[in] amount_centers (uint): Amount of centers that should be initialized.
        @param[in] amount_candidates (uint): Amount of candidates that is considered as a center, if the farthest points
                    (with the highest probability) should be considered as centers then special constant should be used
                    'FARTHEST_CENTER_CANDIDATE'.

        @see FARTHEST_CENTER_CANDIDATE

        """

        self.__data = numpy.array(data)
        self.__amount = amount_centers
        self.__free_indexes = set(range(len(self.__data)))

        if amount_candidates is None:
            self.__candidates = 3
            if self.__candidates > len(self.__data):
                self.__candidates = len(self.__data)
        else:
            self.__candidates = amount_candidates

        self.__check_parameters()

        random.seed()

    def __check_parameters(self):
        """!
        @brief Checks input parameters of the algorithm and if something wrong then corresponding exception is thrown.

        """
        if (self.__amount <= 0) or (self.__amount > len(self.__data)):
            raise ValueError("Amount of cluster centers '" + str(self.__amount) + "' should be at least 1 and "
                                                                                  "should be less or equal to amount of points in data.")

        if self.__candidates != kmeans_plusplus_initializer.FARTHEST_CENTER_CANDIDATE:
            if (self.__candidates <= 0) or (self.__candidates > len(self.__data)):
                raise ValueError("Amount of center candidates '" + str(self.__candidates) + "' should be at least 1 "
                                                                                            "and should be less or equal to amount of points in data.")

        if len(self.__data) == 0:
            raise ValueError("Data is empty.")

    def __calculate_shortest_distances(self, data, centers):
        """!
        @brief Calculates distance from each data point to nearest center.

        @param[in] data (numpy.array): Array of points for that initialization is performed.
        @param[in] centers (numpy.array): Array of indexes that represents centers.

        @return (numpy.array) List of distances to closest center for each data point.

        """

        dataset_differences = numpy.zeros((len(centers), len(data)))
        for index_center in range(len(centers)):
            center = data[centers[index_center]]

            #dataset_differences[index_center] = numpy.sum(numpy.square(data - center), axis=1).T
            dataset_differences[index_center] = (data - center)

        with warnings.catch_warnings():
            numpy.warnings.filterwarnings('ignore', r'All-NaN (slice|axis) encountered')
            shortest_distances = numpy.nanmin(dataset_differences, axis=0)

        return shortest_distances

    def __get_next_center(self, centers):
        """!
        @brief Calculates the next center for the data.

        @param[in] centers (array_like): Current initialized centers represented by indexes.

        @return (array_like) Next initialized center.<br>
                (uint) Index of next initialized center if return_index is True.

        """

        distances = self.__calculate_shortest_distances(self.__data, centers)

        if self.__candidates == kmeans_plusplus_initializer.FARTHEST_CENTER_CANDIDATE:
            for index_point in centers:
                distances[index_point] = numpy.nan
            center_index = numpy.nanargmax(distances)
        else:
            probabilities = self.__calculate_probabilities(distances)
            center_index = self.__get_probable_center(distances, probabilities)

        return center_index

    def __get_initial_center(self, return_index):
        """!
        @brief Choose randomly first center.

        @param[in] return_index (bool): If True then return center's index instead of point.

        @return (array_like) First center.<br>
                (uint) Index of first center.

        """

        index_center = random.randint(0, len(self.__data) - 1)
        if return_index:
            return index_center

        return self.__data[index_center]

    def __calculate_probabilities(self, distances):
        """!
        @brief Calculates cumulative probabilities of being center of each point.

        @param[in] distances (array_like): Distances from each point to closest center.

        @return (array_like) Cumulative probabilities of being center of each point.

        """

        total_distance = numpy.sum(distances)
        if total_distance != 0.0:
            probabilities = distances / total_distance
            return numpy.cumsum(probabilities)
        else:
            return numpy.zeros(len(distances))

    def __get_probable_center(self, distances, probabilities):
        """!
        @brief Calculates the next probable center considering amount candidates.

        @param[in] distances (array_like): Distances from each point to closest center.
        @param[in] probabilities (array_like): Cumulative probabilities of being center of each point.

        @return (uint) Index point that is next initialized center.

        """

        index_best_candidate = 0
        for i in range(self.__candidates):
            candidate_probability = random.random()
            index_candidate = -1

            for index_object in range(len(probabilities)):
                if candidate_probability < probabilities[index_object]:
                    index_candidate = index_object
                    break

            if index_candidate == -1:
                index_best_candidate = next(iter(self.__free_indexes))
            elif distances[index_best_candidate] < distances[index_candidate]:
                index_best_candidate = index_candidate

        return index_best_candidate

    def initialize(self, **kwargs):
        """!
        @brief Calculates initial centers using K-Means++ method.

        @param[in] **kwargs: Arbitrary keyword arguments (available arguments: 'return_index').

        <b>Keyword Args:</b><br>
            - return_index (bool): If True then returns indexes of points from input data instead of points itself.

        @return (list) List of initialized initial centers.
                  If argument 'return_index' is False then returns list of points.
                  If argument 'return_index' is True then returns list of indexes.

        """

        return_index = kwargs.get('return_index', False)

        index_point = self.__get_initial_center(True)
        centers = [index_point]
        self.__free_indexes.remove(index_point)

        # For each next center
        for _ in range(1, self.__amount):
            index_point = self.__get_next_center(centers)
            centers.append(index_point)
            self.__free_indexes.remove(index_point)

        if not return_index:
            centers = [self.__data[index] for index in centers]

        return centers
