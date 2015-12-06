# -*- coding: utf-8 -*-
# author : Hulk
# date : 2015-12-3
# description : Genetic Algorithm

import random
import numpy as np
import csv

######################################################################################################################
#                                       ## 基因编码函数 ##
# Description: 产生4个随机数，转化为17*4位的二进制，拼接在一起组成一个个体的基因
# Return: 返回种群的一个个体基因
# 参数说明:
# None
######################################################################################################################

def GeneCode():
    a = random.randint(0, 100000)
    b = random.randint(0, 200000)
    c = random.randint(0, 100000)
    d = random.randint(0, 200000)
    a = bin(a)[2:].zfill(18)
    b = bin(b)[2:].zfill(18)
    c = bin(c)[2:].zfill(18)
    d = bin(d)[2:].zfill(18)
    individual = a + b + c + d
    return individual


######################################################################################################################
#                                       ## 基因解码函数 ##
# Description: 对于4*17位的二进制，切片成4个二进制数，进一步转化为十进制，
#              然后进一步处理使a, c属于(0, 100), b, d属于(-100, 100)。
# Return: 返回4个参数a, b, c, d
# 参数说明:
# individual: 个体基因
######################################################################################################################

def GeneDecode(individual, length = 18):
    a = individual[0: length]
    b = individual[length: length * 2]
    c = individual[length * 2: length * 3]
    d = individual[length * 3:]
    a = float(int(a, 2))/1000
    b = float((int(b, 2) - 100000)) / 1000
    c = float(int(c, 2))/1000
    d = float((int(d, 2) - 100000)) / 1000
    return a, b, c, d


######################################################################################################################
#                                       ## 产生随机种群函数 ##
# Description: 产生N个个体组成的种群
# Return: 编码后的种群,个体数为N
# 参数说明:
# N：种群个数
######################################################################################################################

def CreatePopulation(N = 20):
    population = []
    for i in range(N):
        population.append(GeneCode())
    return population


######################################################################################################################
#                                       ## 个体评价的适应度函数 ##
# Description: 适应度函数越大，表示绩效评价结果越接近学习样本的评价结果
# Return: 适应度值
# 参数说明:
# individual：种群个体
# input： 投入
# output：产出
# contrastRank：测试样本的排名(numpy数组)
######################################################################################################################

def CalAdaptiveValue(individual, sinput, soutput, contrastRank):
    a, b, c, d = GeneDecode(individual)
    sinput = np.array(sinput)
    soutput = np.array(soutput)
    score = (a * sinput + b) / (c * soutput + d)
    #获得当前分数表各大学对应排名
    curRank = []
    for i in score:
        rank = 1
        for j in score:
            if i < j:
                rank += 1
        curRank.append(rank)
    curRank = np.array(curRank)
    # print 'curRank: ' , curRank
    # print 'conRank: ' , contrastRank
    adaptiveValue = float(1) / float((sum(abs(curRank - contrastRank)) + 1))
    return adaptiveValue


######################################################################################################################
#                                             ## 选择函数 ##
# Description: 轮盘法，保证当前群体中适应度较高的个体有更多的机会遗传到下一代
# Return: 选择繁殖的种群
# 参数说明:
# adaptiveList：当前种群的适应度列表
# population：当前种群
# n：种群数量
######################################################################################################################

def ChoseTheSurvival(population, n, adaptiveList):
    survivalList = []
    sunOfAdaptive = sum(adaptiveList)
    adaptiveRatioArray = np.array(adaptiveList)/sunOfAdaptive
    print 'ratio:', adaptiveRatioArray
    for i in range(n):
        index = 0
        #摇骰子，落在哪个区域就选哪个去交配
        dice = random.random()
        area = 0
        while True:
            area += adaptiveRatioArray[index]
            if dice < area:
                survivalList.append(population[index])
                break
            index += 1
    return survivalList


######################################################################################################################
#                                             ## 交叉运算函数 ##
# Description: 交换染色体，产生新个体
# Return: 下一代种群
# 参数说明:
# population: 当前参与交叉运算的群体
# n: 种群个体数量
######################################################################################################################

def Copulation(population, n):
    #随机排序population
    random.shuffle(population)
    #个体基因长度
    geneLenth = len(population[0])
    for i in range(n/2):
        #交换染色体起始位置
        startLocation = random.randint(0, geneLenth - 1)
        tempChromosome = population[i * 2][startLocation:]
        population[i * 2] = population[i * 2][0: startLocation] + population[i * 2 + 1][startLocation:]
        population[i * 2 + 1] = population[i * 2 + 1][0: startLocation] + tempChromosome
    return population


######################################################################################################################
#                                             ## 变异运算函数 ##
# Description: 随机选择个体，随机选择变异点，random一个数，少于阀值Pm就进行变异
# Return: 变异后种群
# 参数说明:
# population: 当前参与交叉运算的群体
# n: 种群个体数量
######################################################################################################################

def Genovariation(population, n, Pm = 0.05):
    #个体基因长度
    geneLenth = len(population[0]) - 1
    for i in range(n):
        p_variation = random.random()
        #变异
        if p_variation < Pm:
            variationLocation = random.randint(0, geneLenth - 1)
            if population[i][variationLocation] == '1':
                temp = population[i][0:variationLocation] + '0' + population[i][variationLocation + 1:]
                population[i] = temp
            elif population[i][variationLocation] == '0':
                temp = population[i][0:variationLocation] + '1' + population[i][variationLocation + 1:]
                population[i] = temp
    return population


######################################################################################################################
#                                             ## 遗传算法 ##
# 参数说明:
# adaptiveThreshold: 适应度阀值，大于它就输出结果，否则继续迭代
# contrastRank：测试样本的排名
# input： 投入
# output：产出
######################################################################################################################

def Evolution(adaptiveThreshold, sinput, soutput, contrastRank, n = 20):
    #产生随机种群
    population = CreatePopulation(n)
    #啪啪啪
    time = 10000000
    while True:
        adaptiveList = []
        for individual in population:
            adaptiveList.append(CalAdaptiveValue(individual, sinput, soutput, contrastRank))
        maxAdaptiveValue = max(adaptiveList)
        print maxAdaptiveValue
        #种群中最大的个体适应度大于阀值就跳出循环，返回该个体
        if maxAdaptiveValue > adaptiveThreshold:
            return population[adaptiveList.index(maxAdaptiveValue)]
        #选择需要进行交配的新种群，淘汰适应度低的个体
        population = ChoseTheSurvival(population, n, adaptiveList)
        #交配啊杂交啊
        population = Copulation(population, n)
        #变异啊异形啊
        population = Genovariation(population, n)
        time -= 1
        if time == 0:
            break




if __name__ == "__main__":
    lines = csv.reader(file('train.csv', 'rb'))
    sinput = []
    soutput = []
    contrastRank = []
    i = 1
    for line in lines:
        sinput.append(float(line[1]))
        soutput.append(float(line[2]))
        contrastRank.append(i)
        i += 1
    contrastRank = np.array(contrastRank)
    individual = Evolution(0.1, sinput, soutput, contrastRank)

# population = ['111000', '101010', '010101', '000111']
# a = GeneCode()
# GeneDecode(a)