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

#for animating the update functions
render_frame = 0

maxUserID = 0
def getUserID():
    global maxUserID
    maxUserID += 1
    return maxUserID

#keep a graph representation for visualization
G = nx.Graph()
#sets that store the userID of users who have and have not been updated
updated_users = set()
nonupdated_users = set()
idToUser = {}

class User():
    def __init__(self, userID=None):
        global nonupdated_users, idToUser
        if userID:
            self.userID = userID
        else:
            self.userID = getUserID()
        nonupdated_users.add(self.userID)
        idToUser[self.userID] = self
        G.add_node(self.userID)

        self.mentors = {}
        self.students = {}
        self.version = 1.0

    def addStudent(self, student):
        self.students[student.userID] = student
        student.mentors[self.userID] = self
        G.add_edge(self.userID, student.userID)

    def removeStudent(self, student):
        del self.students[student.userID]
        del student.mentors[self.userID]
        G.remove_edge(self.userID, student.userID)

    def isSingleton(self):
        return len(self.students) == 0 and len(self.mentors) == 0

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        #return "mentorIDs: " + ', '.join([str(ID) for ID in self.mentors.keys()]) + '\n' + "studentIDs: " + ', '.join([str(ID) for ID in self.students.keys()])
        return 'userID: {}'.format(self.userID)

def renderGraph(position):
    global render_frame, nonupdated_users, updated_users, G
    plt.figure(figsize=(20,20))
    #nodes
    nx.draw_networkx_nodes(G,position,node_color='b',nodelist=nonupdated_users)
    nx.draw_networkx_nodes(G,position,nodelist=updated_users)
    # edges
    nx.draw_networkx_edges(G,position,width=1)
    # labels
    #nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')

    plt.xlim(-1.1,1.1)
    plt.ylim(-1.1,1.1)
    plt.axis('off')
    plt.savefig('graph_frame{}.png'.format(render_frame), dpi=50)
    plt.close()
    print('rendered frame {}'.format(render_frame))
    render_frame += 1

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

def getAllConnectedGraphs():
    '''
    Get a set of all connected graphs as a list of tuples of the form (arbitrary node inside the connected graph, number of nodes in that graph).
    '''
    result = []

    unvisited = updated_users.union(nonupdated_users)
    while unvisited:
        userID = random.choice(list(unvisited))
        user = idToUser[userID]
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
        #print((user.userID, graph_size))
        #time.sleep(1)
    result.sort(key=lambda tup: tup[1])
    return result


'''
        Total Infection
'''

def totalInfection(patientZero, new_version=2.0, render=True, node_positions=None):
    '''
    Starting from any given user, the entire connected component of the coaching graph containing that user should become infected.
    '''
    #get graph ready to render
    if render and not node_positions:
        node_positions = nx.spring_layout(G,dim=2,k=.1)

    leaves = [patientZero]
    while leaves:
        new_leaves = []
        for leaf in leaves:
            leaf.version = new_version
            updated_users.add(leaf.userID)
            if leaf.userID in nonupdated_users:
                nonupdated_users.remove(leaf.userID)
                #print('updated {}'.format(leaf.userID))
            new_leaves += [user for user in leaf.students.values() if user.version < new_version]
            new_leaves += [user for user in leaf.mentors.values() if user.version < new_version]
        leaves = new_leaves
        if render:
            renderGraph(node_positions)


'''
                Limited Infection
'''

def limitedInfection(target, graphs, new_version=2.0, render=True, allow_over=True, node_positions=None):
    '''
    For the first variation of this algorithm, let's guarantee that a mentor-student relationship will not be divided into the updated and nonupdated. This seems reasonable, as even classroom sizes grow statistically small as our user space grows. If our target is to update 100 users, then a difference of 15 users in either direction is noticeable but still probably fine and worth keeping the user experience consistent in that classroom. If our target is to update 1000 or 10000 students then a difference of that amount becomes statistically insignificant.

    If we don't allow any breaks, then we just want to minimize the difference from the target. So we will update all the singletons first, and then progressively update larger and larger networks until we reach the target, going either over or under it depending on which gets us closer.
    '''
    if render and not node_positions:
        node_positions = nx.spring_layout(G,dim=2,k=.1)

    to_update = []
    update_count = 0
    for graph in graphs:
        if update_count + graph[1] > target:
            if allow_over and abs(target - update_count - graph[1]) < abs(target - update_count):
                update_count += graph[1]
                to_update.append(graph[0])
            break
        update_count += graph[1]
        to_update.append(graph[0])
    print('can update {} users. target: {}'.format(update_count, target))
    for user in to_update:
        totalInfection(user, node_positions=node_positions, render=render)
        #print('infected: {}, uninfected: {}'.format(len(updated_users), len(nonupdated_users)))
    '''
    Here is an example output from a sweep over these possible targets for a generated graph. One thing to notice is because of how the graph is distributed, beyond a certain point the error becomes pretty large, since the largest networks make up a significant percentage of the whole.
    can update 10 users. target: 10
    can update 20 users. target: 20
    can update 30 users. target: 30
    can update 40 users. target: 40
    can update 50 users. target: 50
    can update 63 users. target: 60
    can update 63 users. target: 70
    can update 63 users. target: 80
    can update 63 users. target: 90
    can update 63 users. target: 100
    can update 63 users. target: 110
    can update 63 users. target: 120
    can update 63 users. target: 130
    can update 200 users. target: 140
    can update 200 users. target: 150
    can update 200 users. target: 160
    can update 200 users. target: 170
    can update 200 users. target: 180
    can update 200 users. target: 190
    '''

def limitedInfectionExact(target, graphs, new_version=2.0, render=True):
    '''
    For an exact limited infection, we'll allow for some discontinuities in versions between students and mentors. But we still don't really like it, so we want to minimize this happening. We can measure this by how many edges exist at the end of the algorithm between nodes with different versions, and say that the goal of the algorithm is to minimize that number.

    A fully general and perfect solution would need to rely on graph partitioning, which is NP-hard. I think that's a problem for another day. Instead, let's try to get a decent approximation.

    We'll run the limitedInfection algorithm, which will infect graphs starting at the smallest until all the graphs left would make us go over our target, increasing our error. Then, let's add in a node at a time such that if it's possible to add that node without increasing the number of edges between differently versioned nodes, we'll do it. This will mean a lot of iterating over every node in every graph looking for nodes with only one edge. But we can comfort ourselves with the fact that once we've started adding nodes from a graph, we might get more for free right after.
    '''
    if render:
        node_positions = nx.spring_layout(G,dim=2,k=.1)
    #run limited infection and stay under target
    limitedInfection(target, graphs, allow_over=False, new_version=new_version, render=False)
    #remove updated graphs
    noninfected_graphs = []
    print('the following graphs are still noninfected:')
    for graph in graphs:
        if graph[0].version < new_version:
            nodeset = getConnectedGraph(graph[0])
            noninfected_graphs.append(nodeset)
            print(graph, 'nodeset len:', len(nodeset))
    toehold = None
    while len(updated_users) < target:
        renderGraph(node_positions)
        if not toehold:
            toehold = random.choice(list(noninfected_graphs[0]))
            for nodeset in noninfected_graphs:
                for node in nodeset:
                    #print('node: {},{}   toehold: {},{}'.format(len(node.students), len(node.mentors), len(toehold.students), len(toehold.mentors)))
                    if node.userID not in updated_users and len(node.students) + len(node.mentors) < len(toehold.students) + len(toehold.mentors):
                        toehold = node
        edge_cost = len(toehold.students) + len(toehold.mentors)
        while len(toehold.students) + len(toehold.mentors) <= edge_cost:
            if toehold.userID in nonupdated_users:
                nonupdated_users.remove(toehold.userID)
            updated_users.add(toehold.userID)
            toehold.version = new_version
            toehold = random.choice(list(toehold.students.values()) + list(toehold.mentors.values()))
        #print(toehold.userID, toehold.students, toehold.mentors)
        toehold = None
        print(target - len(updated_users), 'left to go')
        time.sleep(1)

def buildRandomGraph(total_users=100):
    '''
    There are a number of types of site users we're going to model:
    1) classrooms
    2) singletons
    3) poly-connected users (could have any number of mentors / students, or both)

    This code tends to generate many unconnected users, a number of very small graphs, and several small-world networks. This should reflect reality enough for our purposes. We'll only ever run this method before an update, so we can consider the set nonupdated_users as the set of all users.
    '''
    global nonupdated_users, idToUser
    for i in range(total_users):
        user = User()
    for userID in nonupdated_users:
        user = idToUser[userID]
        if user.isSingleton():
            if random.random() < 0.1:
                #classroom users
                students = random.sample(nonupdated_users, 20)
                for studentID in students:
                    student = idToUser[studentID]
                    if student.isSingleton():
                        user.addStudent(student)
            elif random.random() < 0.2: #the connectivity of the graph is very sensitive to how this threshold is defined
                #poly-connected users
                students = random.sample(nonupdated_users, random.randint(0, 3))
                mentors = random.sample(nonupdated_users, random.randint(0, 3))
                for studentID in students:
                    student = idToUser[studentID]
                    user.addStudent(student)
                for mentorID in mentors:
                    mentor = idToUser[mentorID]
                    mentor.addStudent(user)
            else:
                #singleton
                pass

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
limitedInfectionExact(n_users-100, graphs)
