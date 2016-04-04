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

    def neighbors(self):
        return list(self.students.values()) + list(self.mentors.values())

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
    Update a number of users as close as possible to the target without breaking connected graphs into updated / not updated.

    target: the number of users to update
    graphs: an array of tuples returned from getAllConnectedGraphs, of the form (arbitrary node inside the connected graph, number of nodes in that graph) and sorted by the second value from lowest to highest.
    allow_over: if True, allow the number of users updated to exceed the target.
    node_positions: physical layout of the nodes for rendering
    '''
    if render and not node_positions:
        node_positions = nx.spring_layout(G,dim=2,k=.1)
    #remove any networks that are larger than our target
    while graphs[-1][1] > (target - len(updated_users)):
        graphs.pop()
    #update the most-connected graphs until we can't fit anymore
    while graphs[-1][1] < (target - len(updated_users)):
        graph = graphs.pop()
        totalInfection(graph[0], render=render, node_positions=node_positions)
        if render:
            renderGraph(node_positions)
        print('infected: {}'.format(len(updated_users)))
    if len(updated_users) == target:
        return
    #then try updating the least-connected graphs until we finish or can't fit anymore
    to_update = []
    update_count = 0
    target = target-len(updated_users)
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


def limitedInfectionExact(target, graphs, new_version=2.0, render=False):
    '''
    In this algorithm, we'll take advantage of our particular knowledge of the graph: mentors will tend to have many students, but students don't tend to have many mentors. Since we are interested in not separating classrooms by version number, if we choose a random node and update their mentor and their mentor's students, we can get a classroom in a single sweep. If a student has multiple mentors simultaneously, their version might be updated before their peers.

    target: the number of users to update
    graphs: an array of tuples returned from getAllConnectedGraphs, of the form (arbitrary node inside the connected graph, number of nodes in that graph) and sorted by the second value from lowest to highest.
    strict: if True, will raise an error if the exact number of nodes cannot be updated.
    '''
    limitedInfection(target, graphs, new_version=new_version, render=render, allow_over=False)

    if strict and update_count != target:
        #TODO: find more specific error
        raise Error("Can't update the exact number of nodes without cutting into graphs.")

    #okay, we'll have to break apart a single graph now
    while len(updated_users) < target:
        #choose a random node and update all its neighbors. if we chose a student
        #node, then the mentor node will have lots of students. we should update
        #these all at once.
        userID = random.choice(list(nonupdated_users))
        user = idToUser[userID]
        for mentor in user.mentors.values():
            for student in mentor.students.values():
                if student.userID in nonupdated_users:
                    nonupdated_users.remove(student.userID)
                updated_users.add(student.userID)
                student.version = new_version
                if len(updated_users) == target:
                    if render:
                        renderGraph(node_positions)
                    return
            if mentor.userID in nonupdated_users:
                nonupdated_users.remove(mentor.userID)
            updated_users.add(mentor.userID)
            mentor.version = new_version
            if render:
                renderGraph(node_positions)
            if len(updated_users) == target:
                return
            print('{} left'.format(target-len(updated_users)))


def buildRandomGraph(total_users=100):
    '''
    Generate a set of graphs of size total_users.
    '''
    global nonupdated_users, idToUser
    for i in range(total_users):
        user = User()
    for userID in nonupdated_users:
        user = idToUser[userID]
        if user.isSingleton():
            if random.random() < 0.1:
                #classroom users
                students = random.sample(nonupdated_users, min(total_users, 20))
                for studentID in students:
                    student = idToUser[studentID]
                    if student.isSingleton():
                        user.addStudent(student)
            elif random.random() < 0.5: #the connectivity of the graph is very sensitive to how this threshold is defined
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

def reset():
    global render_frame, maxUserID, G, nonupdated_users, updated_users, idToUser
    render_frame = 0
    maxUserID = 0
    G = nx.Graph()
    updated_users = set()
    nonupdated_users = set()
    idToUser = {}

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
limitedInfection(n_users-100, graphs, allow_over=False)

#exact limited infection
#limitedInfectionExactLocal(n_users-100, graphs, render=True)
