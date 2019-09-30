import random
import math
import time
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from calcinterest import *
from poi2group import *
from calcStat import *
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

dfNodesOrignal = dfNodes.copy()
#print(dfNodes.to_string())
#dfNodesAvg['visitDuration'] = np.nan

# construct the [dfNodesAvg] from [dfNodes] where "cost" = "walking time" + "avg. POI visit duration"
for poi in range(len(dfavgDuration)):
    dfNodesOrignal.loc[dfNodesOrignal['to'] == dfavgDuration.poiID[poi], 'cost'] = dfavgDuration.avgDuration[poi]/60 + dfNodesOrignal.cost
    #dfNodesAvg.loc[dfNodesAvg['to'] == dfavgDuration.poiID[poi], 'avgDuration'] = dfavgDuration.avgDuration[poi]/60

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

print('totalLoops: ' + str(totalLoops))
# data frame to hold overall results in the form "algoName", "iteration count", "groupSize", "interest cosine similarity (continuous)", "interest cosine similarity (binary)", "ratio of common top interest"
results = pd.DataFrame(columns=['algo', 'iter', 'groupSize', 'intCosSim', 'intCosSimBin', 'topintRatio', 'intJaccard'])

# iteratively test the various user2group and poi2group algorithms for X no. of times
for loopNo in range(totalLoops):
    resultPOI2GroupRan = pd.DataFrame()
    resultsPOI2GroupRanByDay = pd.DataFrame()
    resultsPOI2GroupKmean = pd.DataFrame()
    print('loopNo: ' + str(loopNo + 1))
    dfNodesAvg = dfNodesOrignal.copy()
    dfInterests = dfIntOriginal.copy()
    #print(dfInterests)
    #print(dfNodesAvg)
    dfInterests = dfInterests.sample(num_of_user_to_select)# randomly select [totalUsers] users from the whole list

    # select the start/end POI and budget based on this current real-life travel sequence
    tempSeqID = dfVisits.seqID.unique()[loopNo]
    tempDfVisits = dfVisits[dfVisits.seqID == tempSeqID]  # get subset of [dfVisits] of this visit sequence [tempSeqID]
    startNode = tempDfVisits['poiID'].iloc[0] # since [dfVisits] is ordered by userID and time, the startNode is the first entry
    endNode = startNode

    # set up endNode profit and visiting time to 0
    startNodeVT = dfavgDuration.loc[dfavgDuration.poiID == startNode].iloc[0]['avgDuration']/60 # calculate endNode visiting time
    dfNodesAvg.loc[dfNodesAvg['to'] == startNode, 'cost'] -= startNodeVT
    dfNodesAvg.loc[dfNodesAvg['to'] == startNode, 'profit'] = 0
    #endNode = tempDfVisits['poiID'].iloc[len(tempDfVisits) - 1] # similarly, endNode is the last entry


    # budget will be the actual distance covered between the POIs in the [tempDfVisits]
    # budget  = random.randrange(5,9,1) * 60 #  budget is randomly selected from 5hr to 8hr
    budget = 0
    for i in range(len(tempDfVisits)-1):
        budget = budget + dfNodesAvg.loc[(dfNodesAvg['from'] == tempDfVisits['poiID'].iloc[i]) & (dfNodesAvg['to'] == tempDfVisits['poiID'].iloc[i+1]), 'cost'].values[0]


    # set the visiting day
    day = 3
    visitedNodePerUsr = {}
    print('budget:'+ str(budget))
    print('startNode:' + str(startNode))
    print('travelDay: ' + str(day))


    # record start time
    rantime = time.time()

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

        # perform the user2group assignment and record the results
        results = results.append(pd.DataFrame([['randomOnce', loopNo, len(groupUserList), calcIntCosSim(groupUserList, dfInterests, True), calcIntCosSim(groupUserList, dfInterests, False), calcTopIntRatio(groupUserList, dfInterests), calcIntJaccard(groupUserList, dfInterests)]], columns = results.columns))
        print(results)
        currentID = nextID

        # perform the poi2group recommendation and record the results
        tempResults = poi2groupOP('clusterOnce', dfNodesAvg, dfInterests, groupUserList, startNode, endNode, budget, day, visitedNodePerUsr)
        tempResults['cluster'] = 'random'
        tempResults['groupID'] = i + 1
        resultPOI2GroupRan = resultPOI2GroupRan.append(tempResults)

    # calculate the running time for random clustering
    rantime = time.time() - rantime


    # record start time
    ranPerDaytime = time.time()
    # random clustering (each day cluster the users)
    dfNodesRandom = dfNodesAvg.copy()
    temVisitingPath = {}
    randUserIDs = list(dfInterests['userID'])
    groupSize = int(math.floor(len(randUserIDs)/groupCount)) # get the approx size of each group
    for travelDay in range(day):
        currentID = 0
        random.shuffle(randUserIDs)

        for i in range(groupCount):
            if i != groupCount:
                nextID = currentID + groupSize
            else:
                nextID = len(randUserIDs)

        #nextID = currentID + groupSize
            groupUserList = randUserIDs[currentID:nextID]  # userIDs of all users in this group
            results = results.append(pd.DataFrame([['randomPerDay', loopNo, len(groupUserList),
                                                    calcIntCosSim(groupUserList, dfInterests, True),
                                                    calcIntCosSim(groupUserList, dfInterests, False),
                                                    calcTopIntRatio(groupUserList, dfInterests),
                                                    calcIntJaccard(groupUserList, dfInterests)]],
                                                  columns=results.columns))
            #print(results)

            currentID = nextID
            temVisitingPath['group' + str(i + 1)] = groupUserList
            tempResults = poi2groupOP('clusterPerDay', dfNodesRandom, dfInterests, temVisitingPath['group' + str(i + 1)], startNode, endNode,
                                         budget, travelDay, visitedNodePerUsr)
            tempResults['groupID'] = (i + 1) * (travelDay + 1)
            resultsPOI2GroupRanByDay = resultsPOI2GroupRanByDay.append(tempResults)
            resultsPOI2GroupRanByDay = resultsPOI2GroupRanByDay.reset_index(drop = True)
            resultsPOI2GroupRanByDay = resultsPOI2GroupRanByDay.sort_values(['groupID', 'day'], ascending=True)


    for user in visitedNodePerUsr.keys():
        visitedNodePerUsr[user].insert(0, startNode)

    resultsPOI2GroupRanByDay = calcStatsRan(visitedNodePerUsr, dfNodesAvg, dfInterests, startNode, budget, day)
    resultsPOI2GroupRanByDay['cluster'] = 'randomByDay'
    # calculate running time for randomByDay clustering
    ranPerDaytime = time.time() - ranPerDaytime

    print(resultsPOI2GroupRanByDay)
    # record start time
    kmeanstime = time.time()
    # kmeans clustering
    dfInt = dfInterests.drop(['userID'], axis=1)
    dfInt = dfInterests.copy()
    kmeans = KMeans(n_clusters=groupCount, random_state=0).fit(dfInt[['Cultural','Amusement', 'Shopping', 'Structure', 'Sport', 'Beach' ]])
    dfInt['groupID'] =  kmeans.labels_
    dfInt = dfInt.sort_values(['groupID'], ascending = True)
    currentID = 0


    for i in range(groupCount):
        groupUserList = []
        for j in range(len(dfInt.index)):
            if dfInt.iloc[j]['groupID'] == i:
                groupUserList.append(dfInt.iloc[j]['userID'])

        results = results.append(pd.DataFrame([['clusterOnceKmeans', loopNo, len(groupUserList),
                                                calcIntCosSim(groupUserList, dfInterests, True),
                                                calcIntCosSim(groupUserList, dfInterests, False),
                                                calcTopIntRatio(groupUserList, dfInterests),
                                                calcIntJaccard(groupUserList, dfInterests)]], columns=results.columns))
        #print(results)

        tempResults = poi2groupOP('clusterOnceKmeans', dfNodesAvg, dfInterests, groupUserList, startNode, endNode, budget, day, visitedNodePerUsr)
        tempResults['cluster'] = 'kMeans'
        tempResults['groupID'] = i + 1
        resultsPOI2GroupKmean = resultsPOI2GroupKmean.append(tempResults)

    # calcualte running time for kmeans clustering
    kmeanstime = time.time() - kmeanstime
    print(resultsPOI2GroupKmean)


    resultsPOI2Group = resultsPOI2Group.append(resultPOI2GroupRan, sort = False)
    resultsPOI2Group = resultsPOI2Group.append(resultsPOI2GroupRanByDay, sort = False)
    resultsPOI2Group = resultsPOI2Group.append(resultsPOI2GroupKmean, sort = False)
    resultsPOI2Group = resultsPOI2Group.reset_index(drop=True)
    results = results.reset_index(drop = True)

    # create new dataframe to do the Average results statistic
    temStatResults = pd.DataFrame()
    temStatResults = temStatResults.append(resultPOI2GroupRan, sort=False)
    temStatResults = temStatResults.append(resultsPOI2GroupRanByDay, sort=False)
    temStatResults = temStatResults.append(resultsPOI2GroupKmean, sort=False)
    print(temStatResults)


    print(resultsPOI2Group)
    print(results)

    resultsMeanTem = calMean(temStatResults, budget,startNode, loopNo, num_of_user_to_select) # various statistic calculation
    resultsMean = resultsMean.append(resultsMeanTem)

resultsPOI2Group.to_csv('recommend_POI_Results.csv', encoding='utf-8') # save the original results
results.to_csv('results_statistics.csv', encoding  = 'utf-8') # save the statistics calculation for groups
resultsMean.to_csv('results_average.csv', encoding  = 'utf-8') # save the average statistics results



    #resultsMean.to_csv('resultsMean.csv', sep='\t', encoding='utf-8')

print(dfInterests)
print(dfNodesAvg)
    #print('random once exc time: ' + str(rantime))
    #print('random per day exc time: ' + str(ranPerDaytime))
    #print('kmeans exc time: ' + str(kmeanstime))

