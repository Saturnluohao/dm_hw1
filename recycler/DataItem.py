import random

import numpy as np
import pandas as pd

class DataItem:
    def __int__(self, vipno, bought_list):
        '''
        :param str vipno:
        :param dict bought_list:
        :return:
        '''
        self.vipno = vipno
        self.bought_list = bought_list
        self.leftOver = False
        self.rightOver = False

    def __str__(self):
        return "{}".format(self.vipno)

    def __sub__(self, other):
        '''
        :param DataItem other
        :return:
        '''
        if not isinstance(other, DataItem):
            return np.nan

        inter = union = 0

        other_cpy = other.bought_list.copy()
        ''':type: pd.Series'''
        other_keyset = other_cpy.keys()
        for i, v in self.bought_list.items():
            if i in other_keyset:
                other_v = other_cpy[i]
                inter += min(v, other_v)
                union += max(v, other_v)
                del other_cpy[i]
            else:
                union += v

        for i, v in other_cpy.items():
            union += v

        #bought_list = pd.merge(self.bought_list, other.bought_list, on='pluno', how='outer')
        ''':type: pd.DataFrame'''

        # bought_list['union'] = bought_list[['amt_x', 'amt_y']].max(axis=1)
        # bought_list['inter'] = bought_list[['amt_x', 'amt_y']].min(axis=1, skipna=False)
        # bought_list['inter'] = bought_list['inter'].map(lambda x : 0 if np.isnan(x) else x)
        #
        # union = bought_list['union'].sum()
        # inter = bought_list['inter'].sum()

        if union != 0:
            return 1 - inter / union
        else:
            return 0


    def __add__(self, right):
        if not isinstance(right, DataItem):
            raise TypeError("DataItem can only be added with DataItem")
        result = {}

        # iter1 = self.bought_list.items().__iter__()
        # iter2 = other.items().__iter__()
        #
        # item1 = (-1, -1)
        # item2 = (-1, -1)
        #
        # initial_empty = False
        #
        # try:
        #     item1 = self.getNext(iter1, True)
        #     item2 = self.getNext(iter2, False)
        # except StopIteration:
        #     initial_empty = True
        #
        # while not initial_empty:
        #     try:
        #         if item1[0] == item2[0]:
        #             result[item1[0]] = item1[1] + item2[1]
        #             item1 = self.getNext(iter1, True)
        #             item2 = self.getNext(iter2, False)
        #         elif item1[0] < item2[0]:
        #             result[item1[0]] = item1[1]
        #             item1 = self.getNext(iter1, True)
        #         else:
        #             result[item2[0]] = item2[1]
        #             item2 = self.getNext(iter2, False)
        #     except StopIteration:
        #         break
        #
        # if self.rightOver:
        #     while True:
        #         try:
        #             item = iter1.__next__()
        #             result[item[0]] = item[1]
        #         except StopIteration:
        #             break
        # else:
        #     while True:
        #         try:
        #             item = iter2.__next__()
        #             result[item[0]] = item[1]
        #         except StopIteration:
        #             break


        left_bought_list_cpy = self.bought_list.copy()
        left_bought_list__keyset = left_bought_list_cpy.keys()

        for i, v in right.bought_list.items():
            if i in left_bought_list__keyset:
                result[i] = v + left_bought_list_cpy.get(i)
                del left_bought_list_cpy[i]
            else:
                result[i] = v

        for i, v in left_bought_list_cpy.items():
            result[i] = v
        addtion =  DataItem()
        addtion.__int__(right.vipno, result)
        return addtion

    # def getNext(self, iter, isLeft):
    #     try:
    #         return iter.__next__()
    #     except StopIteration:
    #         if isLeft:
    #             self.leftOver = True
    #         else:
    #             self.rightOver = True
    #         raise StopIteration

    def __truediv__(self, other):
        for i, v in self.bought_list.items():
            self.bought_list[i] = v / other