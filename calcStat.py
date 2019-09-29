import pandas as pd
from scipy import spatial
from scipy.spatial.distance import cosine
import statistics

def calMean(budget,startNode):
    results = pd.read_csv('resultstest.csv')
    print(results.to_string())
    resultsMean = results.groupby('cluster')['totalPopInt'].sum().reset_index(name='totalprofit')
    print(resultsMean)
    #resultsMean = results.groupby('cluster')['profit'].mean().reset_index(name='avgProfit')
    resultsMean['budget'] = budget
    resultsMean['startNode'] = startNode
    '''
    sum = results.drop_duplicates(subset=['profit'], keep='first')
    sum = sum.groupby('cluster')['profit'].sum().reset_index(name='avgProfit')
    print(sum)
    print(results['profit'].idxmax())
    '''
    print(resultsMean)
    return resultsMean

def calcIntCosSim(userInGroup, dfInterest, binaryInt):
    cosVec =[]
    results = []
    userIntByTime = pd.DataFrame(columns=dfInterest.columns)
    for i in range(len(userInGroup)):
        userIntByTime = userIntByTime.append(dfInterest.loc[dfInterest['userID'] == userInGroup[i]])
    userIntByTime = userIntByTime.drop(['userID'], axis=1)
    print(userIntByTime)
    userIntByTime = userIntByTime.reset_index(drop=True)
    if binaryInt == True:
        userIntByTime[userIntByTime != 0] = 1
    print(userIntByTime)
    for i in range(len(userIntByTime.index)):
        for j in range(len(userIntByTime.index)):
            if i != j:
                cosTem = 1 - cosine(userIntByTime.iloc[i], userIntByTime.iloc[j])
                cosVec.append(cosTem)

    print(len(cosVec))
    print(cosVec)
    cos = statistics.mean(cosVec)
    print(statistics.mean(cosVec))
    return cos


#calMean(budget = 300,startNode=7)
