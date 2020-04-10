import os
import sys
import h5py

import numpy as np
import pandas as pd
import utils as u

from prettytable import PrettyTable

class Counter:
    def __init__(self):
        # self.dataInfo = ['group', 'tcf', 'fit method', 'exponent count', 'success count', 'fail count', 'mean time', 'all time']
        self.dataInfo = ['N', 'group', 'tcf', 'fit method', 'exponent count', 'success rate', 'fit time']
        self.data = pd.DataFrame(columns=self.dataInfo)

        self.cN = 0
        self.cgroup = None
        self.ctcf = None
        self.cmethod = None

    ## Adders
    def add_fitInfo(self, fitInfo_series=None, expCount=None, successRate=None, time=None):
        if fitInfo_series:
            self.data = self.data.append(pd.Series(data={'N':self.cN, 'group': self.cgroup,
               'tcf': self.ctcf,
               'fit method': self.cmethod,
               'exponent count': fitInfo_series.expCount,
               'success rate': fitInfo_series.successRate,
               'fit time': fitInfo_series.fitTime}), ignore_index=True)
        else:
            self.data = self.data.append(pd.Series(data={'N':self.cN, 'group': self.cgroup,
               'tcf': self.ctcf,
               'fit method': self.cmethod,
               'exponent count': expCount,
               'success rate': successRate,
               'fit time': time}), ignore_index=True)

    def set_curGroup(self, cgroup):
        self.cgroup = cgroup

    def set_curTcf(self, ctcf):
        self.ctcf = ctcf

    def set_curMethod(self, cmethod):
        self.cmethod = cmethod

    def set_curN(self, N):
        self.cN = N

    def clean(self):
        pass

    def save(self, filename):
        self.data.to_csv(filename, index=False)

    def get_funcCount(self, group=None, exp=None):
        if group:
            if exp:
                nCount = self.data[(self.data['exponent count'] == exp) & (self.data['group'] == group)]['N'].count()
            else:
                nCount = self.data[(self.data['group'] == group)]['N'].count()
        else:
            nCount = len(self.data['N'].unique())
        return nCount

    def get_allTime(self, group=None, exp=None):
        if group:
            if exp:
                allTime = self.data[(self.data['exponent count'] == exp) & (self.data['group'] == group)]['fit time'].sum()
            else:
                allTime = self.data[(self.data['group'] == group)]['fit time'].sum()
        else:
            allTime = self.data['fit time'].sum()

        return allTime

    def get_meanTime(self, group=None, exp=None):
        if group:
            if exp:
                meanTime = self.data[(self.data['group'] == group) & (self.data['exponent count'] == exp)]['fit time'].mean()
            else:
                meanTime = self.data[(self.data['group'] == group)]['fit time'].mean()
        elif exp:
            meanTime = self.data[(self.data['exponent count'] == exp)]['fit time'].mean()
        else:
            meanTime = self.data['fit time'].mean()
        return meanTime

    def get_successCount(self, group=None, exp=None, function=False):
        if group:
            if exp:
                successRate = self.data[(self.data['group'] == group) & (self.data['exponent count'] == exp)]['success rate'].sum()
            else:
                successRate = self.data[(self.data['group'] == group)]['success rate'].sum()
        else:
            successRate = self.data['success rate'].sum()

        if function:
            successRate = 0
            for n in self.data['N'].unique():
                sR = self.data[(self.data['N'] == n)]['success rate'].sum()
                successRate += 1 if sR else 0
        return successRate

    def __str__(self):
        output = "_________ОБЩАЯ СТАТИСТИКА________\n"
        output += "Общее время работы: {:.3f} c\nЧисло успешно вписанных: {}/{}\nМетод: {}\n".format(self.get_allTime(), self.get_successCount(function=True), self.get_funcCount(), self.cmethod)
        output += "Среднее время работы по числу экспонент:\n"
        for exp in self.data['exponent count'].unique():
            output += '{} - {:.3f} c\n'.format(exp, self.get_meanTime(exp=exp))

        for tcf in self.data['tcf'].unique():
            output += "Корреляционная функция: {}\n"
            x = PrettyTable()
            x.field_names = ['Группа', 'Число Экспонент', 'Среднее время, c', 'Общее время, c', 'Количество успешных']

            for group in self.data['group'].unique():
                for exp in self.data['exponent count'].unique():
                    x.add_row([group, exp, '{:.3f}'.format(self.get_meanTime(group, exp)), '{:.3f}'.format(self.get_allTime(group, exp)), self.get_successCount(group, exp)])
                x.add_row(['Итого', '', '{:.3f}'.format(self.get_meanTime(group)), '{:.3f}'.format(self.get_allTime(group)), "{}/{}".format(self.get_successCount(group), self.get_funcCount(group))])
            output += str(x)
            output += '\n'
        return output

    # def add_successRate(self, sucRate):
        # pass
