# GroupRec
These python codes aim to recommend personalized group tours for different travelling days. We first cluster the users using 2 clustering methods: random & kmeans; and then solve the problem as an integer programming in order to recommend an ideal itinerary to each group. The package we used is pulp.  
The dataset used can be found at https://sites.google.com/site/limkwanhui/datacode#icaps16, which is collected and formed in the following paper.    
1.) Kwan Hui Lim, Jeffrey Chan, Christopher Leckie and Shanika Karunasekera. "Towards Next Generation Touring: Personalized Group Tours". In Proceedings of the 26th International Conference on Automated Planning and Scheduling (ICAPS'16). Pg 412-420. Jun 2016.  

## Included Files
**Code Files**  
tourrecomm.py : The main code which is used to do the pre-processing (forming tour groups whose members have similar interests; decide the travelling day, budget and startNode/endNode).  
poi2group.py: This file is to find the each group's visiting interests from tourrecomm.py, and call the integer progrmming function to do the recommendation.  
tourrecomm.py: This file contains the integer progrmming formulation, including obejctive function, decision variables, and constraints.  
calcinterest.py: This file is used to calculate the average visiting time for each POI.  
calcStat.py: We use this file to do different statistics calculation, such as Cosine similarity, Jaccard similarity.  
**Data Files**  
costProfCat-ToroPOI-all.csv: Sample input data in the form of a cost-profit table, with the following columns/fields: "fromNode", "toNode", "cost", "profit" and "category"  
userVisits-Toro-allPOI.csv: Sample input data in the form of user-POI visits, with the following columns/fields: "photoID", "userID", "dateTaken", "poiID", "poiTheme", "poiFreq", "seqID"  
userInt-URelTime-Toro.csv: Sample input data in the form of user interest levels, with the following columns/fields: "userID", "Cultural", "Amusement", "Shopping", "Structure", "Sport", "Beach"  
## Results Files
recommend_POI_Results.csv:  Calculate statistics of Tour Solution
### Parameters
- 'algo', 'startNode/endNode', 'budget', 'userID', 'totalPOI', 'totalCost', 'totalProfit', 'totalInterest' , 'reachEndNode', 'totalPopInt', 'maxInterest', 'minInterest', 'tour'])
    
