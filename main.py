from MyModel import Classification
from HaoChiUtils import DataAnalyzer as DA
from MainModule import DRI 
import os
from FunctionalInterface import TextEmotionAnalyzer as TEA

if __name__=='__main__':
    tea=TEA()
    uid="7478209878"#测试用例
    tea.assess(uid)