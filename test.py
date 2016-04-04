from infection import *


n_users = 500

buildRandomGraph(n_users)
print('graph generated.')

graphs = getAllConnectedGraphs()
print('got all connected graphs.')

#total infection
#user = graphs[-1][0] #choose a user from the largest connected graph
#totalInfection(user)
#print('infected: {}, uninfected: {}'.format(len(updated_users), len(nonupdated_users)))

#limited infection
#limitedInfection(n_users-1, graphs, allow_over=False)

#exact limited infection
limitedInfectionExactLocal(n_users-100, graphs, render=True)
