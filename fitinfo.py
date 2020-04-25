# import pandas as pd
from timer import Timer

class FitInfo:
    """docstring for FitInfo"""
    def __init__(self, expCount= 0, successRate=False, fitTime=0, output=print):
        self.expCount = expCount
        self.successRate = successRate
        self.fitTime = fitTime
        self.timer = Timer()
        self.output = output

    ### Setters
    def add_successRate(self, successRate):
        self.successRate = successRate
        # if successRate:
        #     self.successCount += 1
        # else:
        #     self.failCount += 1

    def __enter__(self):
        self.timer.start()
        return self

    def __exit__(self, type, value, traceback):
        self.fitTime = self.timer.stop()
        # pd_data = self.to_pdSeries()
        self.output(self)

    def __repr__(self):
        return "FitInfo(expCount: {}, successRate: {}, fitTime: {}, Timer: {})".format(self.expCount, self.successRate, self.fitTime, self.timer)

    ### Export
    def to_pdSeries(self):
        classItems = {key:value for key, value in self.__dict__.items() if not key.startswith('__') and not callable(key)}
