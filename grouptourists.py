import random
import math
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from calcinterest import *
from poi2group import *
from calcStat import *
import csv
# read userid from a csvfile
dfIntOriginal = pd.read_csv('userInt-URelTime-Toro.csv', sep=";")
dfNodes = pd.read_csv("costProfCat-ToroPOI-all.csv", sep=";")
dfVisits = pd.read_csv("userVisits-Toro-allPOI.csv", sep=";")


dfVisitTimes,dfavgDuration = addVisitDuration(dfVisits)
dfVisitTimes.visitDuration = dfVisitTimes.visitDuration/60
dfVisitTimes.avgDuration = dfVisitTimes.avgDuration/60

# only include nodes where we can determine a visitDuration
poiIncludeList = dfVisitTimes['poiID'].unique()
dfNodes['fromisin'] = dfNodes['from'].isin(poiIncludeList)
dfNodes = dfNodes[dfNodes.fromisin]
dfNodes = dfNodes.drop(['fromisin'], axis = 1)

dfNodes['toisin'] = dfNodes['to'].isin(poiIncludeList)
dfNodes = dfNodes[dfNodes.toisin]
dfNodes = dfNodes.drop(['toisin'], axis = 1)

dfNodes.cost = dfNodes.cost * 0.012

dfNodesAvg = dfNodes.copy()
#print(dfNodes.to_string())
#dfNodesAvg['visitDuration'] = np.nan

# construct the [dfNodesAvg] from [dfNodes] where "cost" = "walking time" + "avg. POI visit duration"
for poi in range(len(dfavgDuration)):
    dfNodesAvg.loc[dfNodesAvg['to'] == dfavgDuration.poiID[poi], 'cost'] = dfavgDuration.avgDuration[poi]/60 + dfNodesAvg.cost
    #dfNodesAvg.loc[dfNodesAvg['to'] == dfavgDuration.poiID[poi], 'avgDuration'] = dfavgDuration.avgDuration[poi]/60
#print(dfavgDuration)

# pre-processing
dfVisits = dfVisits.drop_duplicates(subset=['seqID', 'poiID'])
seqCount = dfVisits.groupby(["seqID"]).size().reset_index(name='seqFreq')
dfVisits = dfVisits.merge(seqCount, left_on = 'seqID', right_on = 'seqID')
dfVisits = dfVisits.sort_values(['seqID', 'dateTaken'], ascending = True)
dfVisitsAll = dfVisits
dfVisits = dfVisits[dfVisits.seqFreq>=3]

userID = []
userID_Int = []
num_of_user_to_select = 100  # set the number to select here
groupCount = 5
totalLoops = len(dfVisits.seqID.unique())

# data frame to hold overall results for the poi2group recommendation
resultsMean = pd.DataFrame()
resultsPOI2Group = pd.DataFrame()
resultsPOI2GroupRd1 = pd.DataFrame()
resultsPOI2GroupRd2 = pd.DataFrame()
resultsPOI2GroupKmean = pd.DataFrame()

#for loops in range(2):

# iteratively test the various user2group and poi2group algorithms for X no. of times
#for loopNo in range(totalLoops):
dfInterests = dfIntOriginal
dfInterests = dfInterests.sample(num_of_user_to_select)# randomly select [totalUsers] users from the whole list

# select the start/end POI and budget based on this current real-life travel sequence
tempSeqID = dfVisits.seqID.unique()[0]
tempDfVisits = dfVisits[dfVisits.seqID == tempSeqID]  # get subset of [dfVisits] of this visit sequence [tempSeqID]
startNode = tempDfVisits['poiID'].iloc[0] # since [dfVisits] is ordered by userID and time, the startNode is the first entry
endNode = startNode
#endNode = tempDfVisits['poiID'].iloc[len(tempDfVisits) - 1] # similarly, endNode is the last entry


# budget will be the actual distance covered between the POIs in the [tempDfVisits]
#budget  = random.randrange(5,9,1) * 60 #  budget is randomly selected from 5hr to 8hr
startNodeVT = dfavgDuration.loc[dfavgDuration.poiID == startNode].iloc[0]['avgDuration']/60
budget = 0
#2* dfNodesAvg.loc[dfNodesAvg['to'] == startNode, 'avgDuration'].iloc[0]


for i in range(len(tempDfVisits)-1):
    budget = budget + dfNodesAvg.loc[(dfNodesAvg['from'] == tempDfVisits['poiID'].iloc[i]) & (dfNodesAvg['to'] == tempDfVisits['poiID'].iloc[i+1]), 'cost'].values[0]

print('budget:'+ str(budget))
print('startNode:' + str(startNode))

# set the visiting day
day = 3
'''
# random clustering (cluster only once)
randUserIDs = list(dfInterests['userID'])
random.shuffle(randUserIDs)
groupSize = int(math.floor(len(randUserIDs)/groupCount)) # get the approx size of each group
currentID = 0

for i in range(groupCount):
    if i != groupCount:
        nextID = currentID + groupSize
    else:
        nextID = len(randUserIDs)

#nextID = currentID + groupSize
    groupUserList = randUserIDs[currentID:nextID] # userIDs of all users in this group
    #print(groupUserList)
    currentID = nextID
    tempResults = poi2groupOP(dfNodesAvg, dfInterests, groupUserList, startNode, endNode, budget, day, startNodeVT)
    tempResults['cluster'] = 'random'
    tempResults['groupID'] = i + 1
    resultsPOI2Group = resultsPOI2Group.append(tempResults)

print(resultsPOI2Group)

#print(dfNodesAvg)
'''



print(dfNodesAvg)
# random clustering (each day cluster the users)
dfNodesRandom = dfNodesAvg
temVisitingPath = {}
#visitingPath2 = {}
randUserIDs = list(dfInterests['userID'])
groupSize = int(math.floor(len(randUserIDs)/groupCount)) # get the approx size of each group
visitedNodePerUer = {}
for travelDay in range(2):
    currentID = 0
    random.shuffle(randUserIDs)
    '''
    for i in range(groupCount):
        if i != groupCount:
            nextID = currentID + groupSize
        else:
            nextID = len(randUserIDs)
    '''
    #nextID = currentID + groupSize
    groupUserList = randUserIDs[currentID:20]  # userIDs of all users in this group
    #currentID = nextID
    #temVisitingPath['group' + str(i + 1)] = groupUserList
    print(groupUserList)
    tempResults = Ranpoi2groupOP(dfNodesRandom, dfInterests, groupUserList, startNode, endNode,
                                     budget, travelDay, startNodeVT, visitedNodePerUer)
print(temVisitingPath)

'''
    tempResults = Ranpoi2groupOP(dfNodesRandom, dfInterests, groupUserList, startNode, endNode,
                                  budget, travelDay, startNodeVT)
    tempResults['day'] = 'day1'
    tempResults['cluster'] = 'randomByDay'
    tempResults['groupID'] = i + 1
    resultsPOI2Group = resultsPOI2GroupRd1.append(tempResults)
'''
'''    
        if travelDay == 1:
            visitingPath1['group' + str(i+1)] = groupUserList
        else:
            visitingPath2['group' + str(i+1)] = groupUserList
print(visitingPath1)
print(visitingPath2)

for i in range(groupCount):
    tempResults = poi2groupOP(dfNodesRandom, dfInterests, visitingPath1['group' + str(i+1)], startNode, endNode, budget, 1, startNodeVT)
    tempResults['day'] = 'day1'
    tempResults['cluster'] = 'randomByDay'
    tempResults['groupID'] = i + 1
    resultsPOI2GroupRd1 = resultsPOI2GroupRd1.append(tempResults)

print(resultsPOI2GroupRd1.to_string())



for i in range(groupCount):
    print('i = '+ str(i) )
    visitedNode = []
    for j in range(groupCount):
        if set(visitingPath2['group' + str(i+1)]) & set(visitingPath1['group' + str(j+1)]):
            for index, row in resultsPOI2GroupRd1.iterrows():
                if row['from'] != startNode and row['groupID'] == j + 1:
                    visitedNode.append(row['from'])
        visitedNode = list(dict.fromkeys(visitedNode)) # remove duplicated pois
        for poi in visitedNode:
            dfNodesRandom = dfNodesRandom[dfNodesRandom['from'] != poi]
        for poi in visitedNode:
            dfNodesRandom = dfNodesRandom[dfNodesRandom['to'] != poi]
        dfNodesRandom = dfNodesRandom.reset_index(drop = True)

    print(visitedNode)
    #print(dfNodesRandom)
    tempResults = poi2groupOP(dfNodesRandom, dfInterests, visitingPath2['group' + str(i+1)], startNode, endNode, budget, 1,startNodeVT)
    tempResults['day'] = 'day2'
    tempResults['cluster'] = 'randomByDay'
    tempResults['groupID'] = i + 1
    resultsPOI2GroupRd2 = resultsPOI2GroupRd2.append(tempResults)

resultsPOI2GroupRd1 = resultsPOI2GroupRd1.append(resultsPOI2GroupRd2)

print(visitedNode)


print(resultsPOI2GroupRd1)
'''

'''
print(dfNodesAvg)
# kmeans clustering
dfInt = dfInterests.drop(['userID'], axis=1)
dfInt = dfInterests
kmeans = KMeans(n_clusters=groupCount, random_state=0).fit(dfInt[['Cultural','Amusement', 'Shopping', 'Structure', 'Sport', 'Beach' ]])
dfInt['groupID'] =  kmeans.labels_
dfInt = dfInt.sort_values(['groupID'], ascending = True)
currentID = 0


for i in range(groupCount):
    groupUserList = []
    for j in range(len(dfInt.index)):
        if dfInt.iloc[j]['groupID'] == i:
            groupUserList.append(dfInt.iloc[j]['userID'])
    tempResults = poi2groupOP(dfNodesAvg, dfInterests, groupUserList, startNode, endNode, budget, day, startNodeVT)
    tempResults['cluster'] = 'kMeans'
    tempResults['groupID'] = i + 1
    resultsPOI2GroupKmean = resultsPOI2GroupKmean.append(tempResults)

print(resultsPOI2GroupKmean)

resultsPOI2Group = resultsPOI2Group.append(resultsPOI2GroupRd1)
resultsPOI2Group = resultsPOI2Group.append(resultsPOI2GroupKmean)
'''
'''
resultsPOI2Group.to_csv('resultstest.csv', sep='\t', encoding='utf-8')
resultsMeanTem = calMean(budget,startNode)
resultsMean = resultsMean.append(resultsMeanTem)


resultsMean.to_csv('resultsMean.csv', sep='\t', encoding='utf-8')
'''
