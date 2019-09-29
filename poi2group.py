from tourrecomm import *
from operator import add
from functools import reduce

def poi2groupOP(algo, dfNodes, dfUserInt, groupUserList, startNode, endNode, budget, day, startNodeVT, visitedNodePerUsr):

    results = pd.DataFrame(columns=['algo', 'startNode/endNode', 'budget', 'userID', 'totalPOI', 'totalCost', 'totalProfit', 'totalInterest' , 'reachEndNode', 'totalPopInt', 'maxInterest', 'minInterest', 'tour'])
    userIntByTime = pd.DataFrame(columns=dfUserInt.columns)

    for i in range(len(groupUserList)):
        userIntByTime = userIntByTime.append(dfUserInt.loc[dfUserInt['userID'] == groupUserList[i]])

    userIntByTime = userIntByTime.drop(['userID'], axis = 1)
    userIntByTime = userIntByTime.mean()
    userIntByTime = userIntByTime.reset_index()
    userIntByTime = userIntByTime.rename(columns={'index': 'category', 0: 'catIntLevel'})
    userIntByTime['userID'] = 'group'

    dfNodesPath = dfNodes.copy()
    dfNodesCal = dfNodes.copy()

    if algo == 'clusterOnce' or algo == 'clusterOnceKmeans':
        resultPath = clusterOnceOP(dfNodesPath, startNode, endNode, budget, day, startNodeVT, userIntByTime)
    elif algo == 'clusterPerDay':
        temPath, visitedNodePerUsr = clusterPerDayOP(dfNodes, groupUserList, userIntByTime, startNode, endNode, budget, day, startNodeVT, visitedNodePerUsr)
        print(visitedNodePerUsr)
        return temPath
    '''
    for loop in range(day):
        temPath = tourRecLPmultiObj(startNode, endNode, budget, dfNodesPath, None, userIntByTime, 0.5, False, startNodeVT)
        visitedNode = []
        temPath['day'] = 'day ' + str(loop + 1)
        resultPath = resultPath.append(temPath)
        for index, row in temPath.iterrows():
            if row['from'] != startNode:
                visitedNode.append(row['from'])
        print('visitedNode: '+ str(visitedNode))
        for poi in visitedNode:
            dfNodesPath = dfNodesPath[dfNodesPath['from'] != poi]
        for poi in visitedNode:
            dfNodesPath = dfNodesPath[dfNodesPath['to'] != poi]
        dfNodesPath = dfNodesPath.reset_index(drop=True)
    resultPath = resultPath.reset_index(drop=True)
    '''
    if len(resultPath.index) != 0:
        for tempUserID in groupUserList:
            tempDfUserInt = dfUserInt.loc[dfUserInt['userID'] == tempUserID]  # determine indv user interest
            #print(tempDfUserInt)
            userIntPerUser= pd.melt(tempDfUserInt, id_vars=['userID'], value_vars=['Cultural','Amusement','Shopping','Structure','Sport','Beach']) # determine indv user interest
            userIntPerUser = userIntPerUser.rename(columns={list(userIntPerUser)[0]:'userID', list(userIntPerUser)[1]:'category', list(userIntPerUser)[2]:'catIntLevel'})
            userInterest = userIntPerUser.copy()
            #print(userIntPerUser)
            stats = calcStats(resultPath, dfNodesCal, userInterest, endNode, startNodeVT)
            results = results.append(pd.DataFrame([[algo,startNode,budget,tempUserID,stats.totalPOI.values[0],stats.totalDistance.values[0],stats.totalPopularity.values[0],stats.totalInterest.values[0],stats.completed.values[0],stats.totalPopInt.values[0],stats.maxInterest.values[0],stats.minInterest.values[0],stats.tour.values[0]]], columns = results.columns))
    else:
        for tempUserID in groupUserList:
            tempDfUserInt = dfUserInt.loc[dfUserInt['userID'] == tempUserID]  # determine indv user interest
            userIntPerUser= pd.melt(tempDfUserInt, id_vars=['userID'], value_vars=['Cultural','Amusement','Shopping','Structure','Sport','Beach']) # determine indv user interest
            userIntPerUser = userIntPerUser.rename(columns={list(userIntPerUser)[0]:'userID', list(userIntPerUser)[1]:'category', list(userIntPerUser)[2]:'catIntLevel'})
            results = results.append(pd.DataFrame([[algo,startNode,budget,tempUserID,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]], columns = results.columns))

    results = results.reset_index(drop=True)
    print(results)
    return results


def clusterOnceOP(dfNodesPath, startNode, endNode, budget, day, startNodeVT, userIntByTime):
    resultPath = pd.DataFrame()
    for loop in range(day):
        temPath = tourRecLPmultiObj(startNode, endNode, budget, dfNodesPath, None, userIntByTime, 0.5, False, startNodeVT)
        visitedNode = []
        temPath['day'] = 'day ' + str(loop + 1)
        resultPath = resultPath.append(temPath)
        for index, row in temPath.iterrows():
            if row['from'] != startNode:
                visitedNode.append(row['from'])
        print('visitedNode: '+ str(visitedNode))
        for poi in visitedNode:
            dfNodesPath = dfNodesPath[dfNodesPath['from'] != poi]
        for poi in visitedNode:
            dfNodesPath = dfNodesPath[dfNodesPath['to'] != poi]
        dfNodesPath = dfNodesPath.reset_index(drop=True)
    resultPath = resultPath.reset_index(drop=True)
    return resultPath


def clusterPerDayOP(dfNodesPath, groupUserList, userIntByTime, startNode, endNode, budget, day, startNodeVT, visitedNodePerUsr):

    '''
    userIntByTime = pd.DataFrame(columns=dfUserInt.columns)

    for i in range(len(groupUserList)):
        userIntByTime = userIntByTime.append(dfUserInt.loc[dfUserInt['userID'] == groupUserList[i]])

    userIntByTime = userIntByTime.drop(['userID'], axis = 1)
    userIntByTime = userIntByTime.mean()
    userIntByTime = userIntByTime.reset_index()
    userIntByTime = userIntByTime.rename(columns={'index': 'category', 0: 'catIntLevel'})
    userIntByTime['userID'] = 'group'

    dfNodesPath = dfNodes.copy()
    '''
    visitedNode = []
    for user in groupUserList:
        if user in visitedNodePerUsr.keys():
            print(user)
            visitedNode.append(visitedNodePerUsr[user])
    if len(visitedNode) != 0:
        visitedNode = reduce(add, visitedNode)
        visitedNode = list(dict.fromkeys(visitedNode))
    print(visitedNode)
    for poi in visitedNode:
        if poi != startNode:
            dfNodesPath = dfNodesPath[dfNodesPath['from'] != poi]
    for poi in visitedNode:
        if poi != startNode:
            dfNodesPath = dfNodesPath[dfNodesPath['to'] != poi]
    dfNodesPath = dfNodesPath.reset_index(drop=True)
    print(dfNodesPath)
    ranTemPath = tourRecLPmultiObj(startNode, endNode, budget, dfNodesPath, None, userIntByTime, 0.5, False, startNodeVT)
    ranTemPath['day'] = 'day ' + str(day + 1)
    #visitedNodePerUer = {}
    # store user's visited nodes
    for user in groupUserList:
        if ranTemPath.empty is False:
            for poi in ranTemPath.to:
                #if poi != startNode:
                    visitedNodePerUsr.setdefault(user, [])
                    visitedNodePerUsr[user].append(poi)

    print(visitedNodePerUsr)
    print(len(visitedNodePerUsr))
    return ranTemPath, visitedNodePerUsr


# calculate the statistic for each user in random and kmeans clustering
def calcStats(solnRecTour, dfNodes, userInterest, endNode, startNodeVT):


    dfNodes.profit = dfNodes.profit / max(dfNodes.profit)
    userInterest.catIntLevel = userInterest.catIntLevel / max(userInterest.catIntLevel)
    print(userInterest)

    # calculate the total popularity and interest for the entire tour
    totalPOI = len(solnRecTour.index) - 1
    totalDistance = 0
    totalPopularity = 0
    totalInterest = 0
    totalPopInt = 0
    interestLevels = []
    tour = []
    for i in range(len(solnRecTour.index)):
        tempFrom = solnRecTour.iloc[i]['from']
        tempTo = solnRecTour.iloc[i]['to']
        tempCost = dfNodes.loc[(dfNodes['from'] == tempFrom) & (dfNodes['to'] == tempTo), 'cost'].values[0]

        tempProfit = dfNodes.loc[(dfNodes['from'] == tempFrom) & (dfNodes['to'] == tempTo), 'profit'].values[0]

        tempCategory = dfNodes.loc[(dfNodes['from'] == tempFrom) & (dfNodes['to'] == tempTo), 'category'].values[0]

        totalDistance = totalDistance + tempCost
        totalPopularity = totalPopularity + tempProfit
        if tempCategory in list(userInterest['category']):
            totalInterest = totalInterest + userInterest.loc[userInterest['category'] == tempCategory, "catIntLevel"].values[0]
            interestLevels.append(userInterest.loc[userInterest['category'] == tempCategory, "catIntLevel"].values[0])
        tour.append(tempFrom)
    tour.append(solnRecTour.iloc[len(solnRecTour.index) -1]['to'])
    tour = '-'.join(str(poi) for poi in tour)
    totalPopInt = 0.5 * totalPopularity + 0.5 * totalInterest
    completed = (solnRecTour.iloc[len(solnRecTour.index)-1]['to'] == endNode) & (len(solnRecTour.index) != 0)
    stats = pd.DataFrame([[totalPOI, totalDistance, totalPopularity, totalInterest, completed, totalPopInt, max(interestLevels), min(interestLevels), tour]], columns=['totalPOI', 'totalDistance', 'totalPopularity', 'totalInterest', 'completed', 'totalPopInt', 'maxInterest', 'minInterest', 'tour'])
    print(stats)
    return stats

# calculate the statistics for groups that users are clustered everyday
def calcStatsRan(visitedNodePerUsr, dfNodes, dfUserInt, startNode, budget):


    results = pd.DataFrame(columns=['algo', 'startNode/endNode', 'budget', 'userID', 'totalPOI', 'totalCost', 'totalProfit',
                 'totalInterest', 'reachEndNode', 'totalPopInt', 'maxInterest', 'minInterest', 'tour'])

    for user in visitedNodePerUsr.keys():
        tempDfUserInt = dfUserInt.loc[dfUserInt['userID'] == user]
        userIntPerUser = pd.melt(tempDfUserInt, id_vars=['userID'], value_vars=['Cultural', 'Amusement', 'Shopping', 'Structure', 'Sport', 'Beach'])  # determine indv user interest
        userIntPerUser = userIntPerUser.rename(columns={list(userIntPerUser)[0]: 'userID', list(userIntPerUser)[1]: 'category', list(userIntPerUser)[2]: 'catIntLevel'})
        userInterest = userIntPerUser.copy()
        dfNodesCal = dfNodes.copy()

        dfNodesCal.profit = dfNodesCal.profit / max(dfNodesCal.profit)
        userInterest.catIntLevel = userInterest.catIntLevel / max(userInterest.catIntLevel)

        totalDistance = 0
        totalPopularity = 0
        totalInterest = 0
        totalPopInt = 0
        interestLevels = []
        indvUsrPath = visitedNodePerUsr[user]
        totalPOI = len(indvUsrPath) - 4
        print(indvUsrPath)
        for i in range(len(indvUsrPath) - 1):
            tempFrom = indvUsrPath[i]
            tempTo = indvUsrPath[i + 1]
            tempCost = dfNodesCal.loc[(dfNodesCal['from'] == tempFrom) & (dfNodesCal['to'] == tempTo), 'cost'].values[0]

            tempProfit = dfNodesCal.loc[(dfNodesCal['from'] == tempFrom) & (dfNodesCal['to'] == tempTo), 'profit'].values[0]

            tempCategory = dfNodesCal.loc[(dfNodesCal['from'] == tempFrom) & (dfNodesCal['to'] == tempTo), 'category'].values[0]
            print('totalcost: ' + str(tempCost))
            totalDistance = totalDistance + tempCost
            totalPopularity = totalPopularity + tempProfit
            if tempCategory in list(userInterest['category']):
                totalInterest = totalInterest + userInterest.loc[userInterest['category'] == tempCategory, "catIntLevel"].values[0]
                interestLevels.append(userInterest.loc[userInterest['category'] == tempCategory, "catIntLevel"].values[0])
                print(interestLevels)
            totalPopInt = 0.5 * totalPopularity + 0.5 * totalInterest
            completed = True
        tour = '-'.join(str(poi) for poi in indvUsrPath)
        stats = pd.DataFrame([[totalPOI, totalDistance, totalPopularity, totalInterest, completed, totalPopInt, max(interestLevels), min(interestLevels), tour]], columns=['totalPOI', 'totalDistance', 'totalPopularity', 'totalInterest', 'completed', 'totalPopInt', 'maxInterest', 'minInterest', 'tour'])
        results = results.append(pd.DataFrame([['ClusterPerDay', startNode, budget, user, stats.totalPOI.values[0],
                                      stats.totalDistance.values[0], stats.totalPopularity.values[0],
                                      stats.totalInterest.values[0], stats.completed.values[0],
                                      stats.totalPopInt.values[0], stats.maxInterest.values[0],
                                      stats.minInterest.values[0], stats.tour.values[0]]], columns=results.columns))

    results = results.reset_index(drop=True)
    print(results)
    return results
