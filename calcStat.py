import pandas as pd

def calMean(budget,startNode):
    results = pd.read_csv('resultstest.csv', sep="\t")
    print(results.to_string())
    resultsMean = results.groupby('cluster')['profit'].mean().reset_index(name='avgProfit')
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

#calMean(budget = 300,startNode=7)