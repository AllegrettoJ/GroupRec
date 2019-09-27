from tourrecomm import *
import random
import numpy as np
def poi2groupOP(dfNodes, dfUserInt, groupUserList, startNode, endNode, budget, day, startNodeVT):

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

    if len(resultPath.index) != 0:
        for tempUserID in groupUserList:
            tempDfUserInt = dfUserInt.loc[dfUserInt['userID'] == tempUserID]  # determine indv user interest
            #print(tempDfUserInt)
            userIntPerUser= pd.melt(tempDfUserInt, id_vars=['userID'], value_vars=['Cultural','Amusement','Shopping','Structure','Sport','Beach']) # determine indv user interest
            userIntPerUser = userIntPerUser.rename(columns={list(userIntPerUser)[0]:'userID', list(userIntPerUser)[1]:'category', list(userIntPerUser)[2]:'catIntLevel'})
            userInterest = userIntPerUser.copy()
            #print(userIntPerUser)
            stats = calcStats(resultPath, dfNodesCal, userInterest, endNode, startNodeVT)
            results = results.append(pd.DataFrame([['resultPath',startNode,budget,tempUserID,stats.totalPOI.values[0],stats.totalDistance.values[0],stats.totalPopularity.values[0],stats.totalInterest.values[0],stats.completed.values[0],stats.totalPopInt.values[0],stats.maxInterest.values[0],stats.minInterest.values[0],stats.tour.values[0]]], columns = results.columns))
    results = results.reset_index(drop = True)
    print(results)

    '''
    else {
    for (tempUserID in groupUserList) {
    tempDfUserInt = dfUserInt[dfUserInt$userID == tempUserID, ]  # determine indv user interest
    userIntPerUser = melt(tempDfUserInt, id.vars=c("userID"))  # determine indv user interest
    names(userIntPerUser) = c("userID", "category", "catIntLevel")  # determine indv user interest
    results = rbind(results, data.frame(algo="tourRecLPmultiObjIntTime_i1", startNode=startNode, endNode=endNode, budget=budget, userID=tempUserID, totalPOI=NA, totalCost=NA, totalProfit=NA, totalInterest=NA, reachEndNode=NA, totalPopInt=NA, maxInterest=NA, minInterest=NA, tour=NA) )
    }
    }
    '''
    return resultPath

def Ranpoi2groupOP(dfNodes, dfUserInt, groupUserList, startNode, endNode, budget, day, startNodeVT):
    userIntByTime = pd.DataFrame(columns=dfUserInt.columns)

    for i in range(len(groupUserList)):
        userIntByTime = userIntByTime.append(dfUserInt.loc[dfUserInt['userID'] == groupUserList[i]])

    userIntByTime = userIntByTime.drop(['userID'], axis=1)
    userIntByTime = userIntByTime.mean()
    userIntByTime = userIntByTime.reset_index()
    userIntByTime = userIntByTime.rename(columns={'index': 'category', 0: 'catIntLevel'})
    userIntByTime['userID'] = 'group'

    dfNodesPath = dfNodes.copy()
    RantemPath = tourRecLPmultiObj(startNode, endNode, budget, dfNodesPath, None, userIntByTime, 0.5, False, startNodeVT)
    return RantemPath



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
    totalPopInt = 0.5 * totalPopularity + 0.5 * totalInterest
    completed = (solnRecTour.iloc[len(solnRecTour.index)-1]['to'] == endNode) & (len(solnRecTour.index) != 0)
    stats = pd.DataFrame([[totalPOI, totalDistance, totalPopularity, totalInterest, completed, totalPopInt, max(interestLevels), min(interestLevels), tour]], columns=['totalPOI', 'totalDistance', 'totalPopularity', 'totalInterest', 'completed', 'totalPopInt', 'maxInterest', 'minInterest', 'tour'])
    print(stats)
    return stats






    '''
        if ( tempCategory % in % userInterest$category ) {
        totalInterest = totalInterest + userInterest[userInterest$category == tempCategory, "catIntLevel"]
        interestLevels = c(interestLevels, userInterest[userInterest$category == tempCategory, "catIntLevel"])

        tour = c(tour, tempFrom)
    '''

        #results = solnLPmultiObjIntTime_i1.append(solnLPmultiObjIntTime_i2, sort=False)

'''
    solnLPmultiObjIntTime_i1 = tourRecLPmultiObj(startNode, endNode, budget, dfNodes, None, userIntByTime, 0.5, False)
    results = solnLPmultiObjIntTime_i1.reset_index(drop=True)
    return results
'''

'''
    if day == 1:
        solnLPmultiObjIntTime_i1 = tourRecLPmultiObj(startNode, endNode, budget, dfNodes, None, userIntByTime, 0.5, False)
        results = solnLPmultiObjIntTime_i1.reset_index(drop = True)
        return results

    else:
        # construct the first day's path
        solnLPmultiObjIntTime_i1 = tourRecLPmultiObj(startNode, endNode, budget, dfNodes, None, userIntByTime, 0.5,
                                                     False)
        # remove the visited pois
        visitedNode = []
        for index, row in solnLPmultiObjIntTime_i1.iterrows():
            if row['from'] != startNode:
                visitedNode.append(row['from'])
                print(row['from'])
        print(visitedNode)
        for poi in visitedNode:
            dfNodes = dfNodes[dfNodes['from'] != poi]
        for poi in visitedNode:
            dfNodes = dfNodes[dfNodes['to'] != poi]
        dfNodes = dfNodes.reset_index(drop=True)

        # construct the second day's path
        solnLPmultiObjIntTime_i2 = tourRecLPmultiObj(startNode, endNode, budget, dfNodes, None, userIntByTime, 0.5,
                                                     False)
        # print(solnLPmultiObjIntTime_i1)
        # print(solnLPmultiObjIntTime_i2)
        # reset the index of each day's path and combine them into 1 dataframe
        solnLPmultiObjIntTime_i1['day'] = 'day1'
        solnLPmultiObjIntTime_i1 = solnLPmultiObjIntTime_i1.reset_index(drop=True)
        solnLPmultiObjIntTime_i2['day'] = 'day2'
        solnLPmultiObjIntTime_i2 = solnLPmultiObjIntTime_i2.reset_index(drop=True)

        results = solnLPmultiObjIntTime_i1.append(solnLPmultiObjIntTime_i2, sort=False)

        return results
'''
