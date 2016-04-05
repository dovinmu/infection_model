from infection import *

def runTotalInfection(render=False):
    n_users = 250
    print('\t Total Infection.\nnodes: {}'.format(n_users))
    state = State()
    buildRandomGraph(state, n_users, connectivity=0.2, classrooms=0.1)
    print('graph generated.')
    graphs = getAllConnectedGraphs(state)
    print('got all connected graphs.')
    user = graphs[-1][0] #choose a user from the largest connected graph
    totalInfection(user, state, render=render)
    print('infected: {} of total {}\n'.format(len(state.updated_users), len(state.updated_users) + len(state.nonupdated_users)))

def runLimitedInfection(render=False):
    #recreates the conditions for the second gif in the README
    n_users = 250
    target = 200
    print('\t Limited Infection.\nnodes: {} target: {}'.format(n_users, target))
    state = State()
    buildRandomGraph(state, n_users, connectivity=0.2, classrooms=0.2)
    print('graph generated.')
    graphs = getAllConnectedGraphs(state)
    print('got all connected graphs.')
    limitedInfection(target, graphs, state, render=render)
    print('infected: {}, target: {}\n'.format(len(state.updated_users), target))


def runLimitedInfectionExact(render=False):
    #recreates the last gif in the README
    n_users = 250
    target = 200
    print('\t Exact Limited Infection \n(with high connectivity to better demonstrate)\nnodes: {} target: {}.'.format(n_users, target))
    state = State()
    buildRandomGraph(state, n_users, 0.6, require_singleton=False)
    print('graph generated.')
    graphs = getAllConnectedGraphs(state)
    print('got all connected graphs.')
    limitedInfectionExact(target, graphs, state, render=render)
    print('infected: {}, target: {}\n'.format(len(state.updated_users), target))

def runLimitedInfectionExactBreak(render=False):
    #attempts to break the exact algorithm
    n_users = 250
    target = 251
    print('\t Exact Limited Infection (incorrect input)\nnodes: {} target: {}.'.format(n_users, target))
    state = State()
    buildRandomGraph(state, n_users, 0.6, require_singleton=False)
    print('graph generated.')
    graphs = getAllConnectedGraphs(state)
    print('got all connected graphs.')
    limitedInfectionExact(target, graphs, state, render=render)
    print('infected: {}, target: {}\n'.format(len(state.updated_users), target))


if __name__ == "__main__":
    runTotalInfection()
    runLimitedInfection()
    runLimitedInfectionExact()
    print('break:')
    runLimitedInfectionExactBreak()
