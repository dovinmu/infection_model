'''
Overall instructions:
Write total_infection and limited_infection in your preferred language. Provide tests and instructions for running them.

Total Infection:
When rolling out big new features, we like to enable them slowly, starting with just the KA team, then a handful of users, then some more users, and so on, until we’ve ramped up to 100%. This insulates the majority of users from bad bugs that crop up early in the life of a feature.

Ideally we would like every user in any given classroom to be using the same version of the site. Enter “infections”. We can use the heuristic that each teacher­student pair should be on the same version of the site. So if A coaches B and we want to give A a new feature, then B should also get the new feature. Note that infections are transitive ­ if B coaches C, then C should get the new feature as well. Also, infections are transferred by both the “coaches” and “is coached by” relations.

Starting from any given user, the entire connected component of the coaching graph containing that user should become infected.


Limited Infection:
We would like to be able to infect close to a given number of users. Ideally we'd like a coach and all of their students to either have a feature or not. However, that might not always be possible.

Implement a procedure for limited infection. You will not be penalized for interpreting the specification as you see fit. There are many design choices and tradeoffs, so be prepared to justify your decisions.
'''
import random
import time
import networkx as nx
import matplotlib.pyplot as plt


class State():
    def __init__(self):
        #for animating the update functions
        self.render_frame = 0

        self.maxUserID = 0
        #keep a graph representation for visualization
        self.G = nx.Graph()
        #sets that store the userID of users who have and have not been updated
        self.updated_users = set()
        self.nonupdated_users = set()
        self.idToUser = {}

    def getUserID(self):
        self.maxUserID += 1
        return self.maxUserID


class User():
    def __init__(self, state, userID=None):
        if userID:
            self.userID = userID
        else:
            self.userID = state.getUserID()
        state.nonupdated_users.add(self.userID)
        state.idToUser[self.userID] = self
        state.G.add_node(self.userID)

        self.mentors = {}
        self.students = {}
        self.version = 1.0

    def addStudent(self, student, state):
        self.students[student.userID] = student
        student.mentors[self.userID] = self
        state.G.add_edge(self.userID, student.userID)

    def removeStudent(self, student):
        del self.students[student.userID]
        del student.mentors[self.userID]
        state.G.remove_edge(self.userID, student.userID)

    def neighbors(self):
        return list(self.students.values()) + list(self.mentors.values())

    def isSingleton(self):
        return len(self.students) == 0 and len(self.mentors) == 0

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'userID: {}'.format(self.userID)

def renderGraph(position, state):
    plt.figure(figsize=(20,20))
    #nodes
    nx.draw_networkx_nodes(state.G, position, node_color='b', nodelist=state.nonupdated_users)
    nx.draw_networkx_nodes(state.G, position,nodelist=state.updated_users)
    # edges
    nx.draw_networkx_edges(state.G, position,width=1)

    plt.xlim(-1.1,1.1)
    plt.ylim(-1.1,1.1)
    plt.axis('off')
    plt.savefig('graph_frame{}.png'.format(state.render_frame), dpi=50)
    plt.close()
    print('rendered frame {}'.format(state.render_frame))
    state.render_frame += 1

def getConnectedGraph(user):
    '''
    Get the set of all nodes in the graph.
    '''
    result = set()

    leaves = [user]
    while leaves:
        new_leaves = []
        for leaf in leaves:
            result.add(leaf)
            new_leaves += [user for user in leaf.students.values() if user not in result]
            new_leaves += [user for user in leaf.mentors.values() if user not in result]
        leaves = new_leaves
    return result

def getAllConnectedGraphs(state):
    '''
    Get a set of all connected graphs as a list of tuples of the form (arbitrary node inside the connected graph, number of nodes in that graph).
    '''
    result = []

    unvisited = state.updated_users.union(state.nonupdated_users)
    while unvisited:
        userID = random.choice(list(unvisited))
        user = state.idToUser[userID]
        graph_size = 0

        visited = set()
        leaves = [user]
        while leaves:
            new_leaves = []
            for leaf in leaves:
                if leaf.userID in unvisited: #allows for multiple connections to the node to be explored on a single pass
                    unvisited.remove(leaf.userID)
                    graph_size += 1
                new_leaves += [user for user in leaf.students.values() if user.userID in unvisited]
                new_leaves += [user for user in leaf.mentors.values() if user.userID in unvisited]
            leaves = new_leaves
        result.append((user, graph_size))
    result.sort(key=lambda tup: tup[1])
    return result


'''
        Total Infection
'''

def totalInfection(patientZero, state, new_version=2.0, render=True, node_positions=None):
    '''
    Starting from any given user, the entire connected component of the coaching graph containing that user should become infected.
    '''
    #get graph ready to render
    if render and not node_positions:
        node_positions = nx.spring_layout(state.G,dim=2,k=.1)

    leaves = [patientZero]
    while leaves:
        new_leaves = []
        for leaf in leaves:
            leaf.version = new_version
            state.updated_users.add(leaf.userID)
            if leaf.userID in state.nonupdated_users:
                state.nonupdated_users.remove(leaf.userID)
                #print('updated {}'.format(leaf.userID))
            new_leaves += [user for user in leaf.students.values() if user.version < new_version]
            new_leaves += [user for user in leaf.mentors.values() if user.version < new_version]
        leaves = new_leaves
        if render:
            renderGraph(node_positions, state)


'''
                Limited Infection
'''

def limitedInfection(target, graphs, state, new_version=2.0, render=True, allow_over=True, node_positions=None):
    '''
    Update a number of users as close as possible to the target without breaking connected graphs into updated / not updated.

    target: the number of users to update
    graphs: an array of tuples returned from getAllConnectedGraphs, of the form (arbitrary node inside the connected graph, number of nodes in that graph) and sorted by the second value from lowest to highest.
    allow_over: if True, allow the number of users updated to exceed the target.
    node_positions: physical layout of the nodes for rendering
    '''
    if render and not node_positions:
        node_positions = nx.spring_layout(state.G,dim=2,k=.1)
    #remove any networks that are larger than our target
    while graphs and graphs[-1][1] > (target - len(state.updated_users)):
        graphs.pop()
    #update the most-connected graphs until we can't fit anymore
    while graphs and graphs[-1][1] < (target - len(state.updated_users)):
        graph = graphs.pop()
        totalInfection(graph[0], state, render=render, node_positions=node_positions)
        print('infected graph of size: {}'.format(graph[1]))
    if len(state.updated_users) == target:
        return
    #then try updating the least-connected graphs until we finish or can't fit anymore
    to_update = []
    update_count = 0
    target = target-len(state.updated_users)
    for graph in graphs:
        if update_count + graph[1] > target:
            if allow_over and abs(target - update_count - graph[1]) < abs(target - update_count):
                update_count += graph[1]
                to_update.append(graph[0])
            break
        update_count += graph[1]
        to_update.append(graph[0])
    print('can update {} users from least-connected graphs. target: {}'.format(update_count, target))
    for user in to_update:
        totalInfection(user, state, node_positions=node_positions, render=render)

def limitedInfectionExact(target, graphs, state, new_version=2.0, render=False, strict=False):
    '''
    In this algorithm, we'll take advantage of our particular knowledge of the graph: mentors will tend to have many students, but students don't tend to have many mentors. Since we are interested in not separating classrooms by version number, if we choose a random node and update their mentor and their mentor's students, we can get a classroom in a single sweep. If a student has multiple mentors simultaneously, their version might be updated before their peers.

    target: the number of users to update
    graphs: an array of tuples returned from getAllConnectedGraphs, of the form (arbitrary node inside the connected graph, number of nodes in that graph) and sorted by the second value from lowest to highest.
    strict: if True, will raise an error if the exact number of nodes cannot be updated.
    '''
    if render:
        node_positions = nx.spring_layout(state.G,dim=2,k=.1)
    else:
        node_positions = None

    limitedInfection(target, graphs, state, new_version=new_version, render=render, allow_over=False, node_positions=node_positions)

    if strict and update_count != target:
        #TODO: find more specific exception
        raise Exception("Can't update the exact number of nodes without cutting into graphs.")
    print("Updating parts of a graph.")
    #okay, we'll have to break apart a single graph now
    while len(state.updated_users) < target:
        #choose a random node and update all its neighbors. if we chose a student
        #node, then the mentor node will have lots of students. we should update
        #these all at once.
        userID = random.choice(list(state.nonupdated_users))
        user = state.idToUser[userID]
        for mentor in user.mentors.values():
            for student in mentor.students.values():
                if student.userID in state.nonupdated_users:
                    state.nonupdated_users.remove(student.userID)
                state.updated_users.add(student.userID)
                student.version = new_version
                if len(state.updated_users) == target:
                    if render:
                        renderGraph(node_positions, state)
                    return
            if mentor.userID in state.nonupdated_users:
                state.nonupdated_users.remove(mentor.userID)
            state.updated_users.add(mentor.userID)
            mentor.version = new_version
            if render:
                renderGraph(node_positions, state)
            if len(state.updated_users) == target:
                return


def buildRandomGraph(state, total_users=100, connectivity=0.1, classrooms=0.1, require_singleton=True):
    '''
    Generate a set of graphs of size total_users.
    '''
    for i in range(total_users):
        user = User(state)
    for userID in state.nonupdated_users:
        user = state.idToUser[userID]
        if not require_singleton or user.isSingleton():
            if random.random() < classrooms:
                #classroom users
                students = random.sample(state.nonupdated_users, min(total_users, 20))
                for studentID in students:
                    student = state.idToUser[studentID]
                    if student.isSingleton():
                        user.addStudent(student, state)
            elif random.random() < connectivity: #the connectivity of the graph is very sensitive to how this threshold is defined
                #poly-connected users
                students = random.sample(state.nonupdated_users, random.randint(0, 3))
                mentors = random.sample(state.nonupdated_users, random.randint(0, 3))
                for studentID in students:
                    student = state.idToUser[studentID]
                    user.addStudent(student, state)
                for mentorID in mentors:
                    mentor = state.idToUser[mentorID]
                    mentor.addStudent(user, state)
            else:
                #singleton
                pass
