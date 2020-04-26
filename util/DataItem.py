import numpy as np

class DataItem:
    def __init__(self, vipno, bought_list_by_levels):
        '''
        :param str vipno:
        :param [dict] bought_list_by_levels:
        '''
        self.vipno = vipno
        self.bought_list_by_levels = bought_list_by_levels

    def __sub__(self, other):
        '''
        :param DataItem other:
        :return:
        '''
        if not isinstance(other, DataItem):
            raise TypeError("DataItem can only do subscraption with DataItem")
        dis = 0
        for i in range(len(self.bought_list_by_levels)):
            dis += self.get_distance_by_level(self.bought_list_by_levels[i], other.bought_list_by_levels[i])

        dis  /= len(self.bought_list_by_levels)
        return dis


    def get_distance_by_level(self, left, right):
        inter = union = 0

        right_cpy = right.copy()
        ''':type: dict'''
        right_keyset = right_cpy.keys()
        for i, v in left.items():
            if i in right_keyset:
                right_v = right_cpy[i]
                inter += min(v, right_v)
                union += max(v, right_v)
                del right_cpy[i]
            else:
                union += v

        for i, v in right_cpy.items():
            union += v

        if union != 0:
            return 1 - inter / union
        else:
            return 0

    def __add__(self, other):
        if not isinstance(other, DataItem):
            raise TypeError("DataItem can only be added with DataItem")
        length = len(self.bought_list_by_levels)
        result = [{}] * length

        for i in range(length):
            result[i] = self.get_union_by_level(self.bought_list_by_levels[i], other.bought_list_by_levels[i])

        addition = DataItem(other.vipno, result)
        return addition


    def get_union_by_level(self, left, right):
        '''
        :param dict left:
        :param dict right:
        :return:
        '''
        result = {}

        right_cpy = right.copy()
        right__keyset = right_cpy.keys()

        for i, v in left.items():
            if i in right__keyset:
                result[i] = v + right_cpy.get(i)
                del right_cpy[i]
            else:
                result[i] = v

        for i, v in right_cpy.items():
            result[i] = v
        return result

    def __truediv__(self, other):
        for i in range(len(self.bought_list_by_levels)):
            dicti = self.bought_list_by_levels[i]
            for i, v in dicti.items():
                dicti[i] = v / other