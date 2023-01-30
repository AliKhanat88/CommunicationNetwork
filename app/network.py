from registry import Registry, RegistryException
from messaging import Priority
from collections import defaultdict

class InvalidNetworkException(Exception):
    """
    A generic exception for problems in the network
    """
    pass

class Node:
    def __init__(self, node_id):
        """
        Default constructor. If you need to set attributed, use explicit setters/getters. Do not add parameters here
        :param node_id:
        """
        # Data members
        self.node_id = node_id  
        # for the all messages at a purticular node
        # Format: person_if -> list of messages
        self.messages = defaultdict(lambda: [])

    # Being checked in test_smoke_tests.py
    def receive(self, message):
        """
        Receive a message
        :param message: an object with sender, priority, content, and recipient fields
        :return:
        """
        # if none it means message is boradcasted and needs to be send to everyone
        if message.receiver is None:
            all_person_list = self.network._registry.database[self.node_id] # getting list of persons on that node
            for key in all_person_list:
                # check is person same as sender?
                if message.sender != key:
                    self.messages[key].append(message)
        else:
            # if not then only send message to the node
            self.messages[message.receiver].append(message)

    # Being checked in test_smoke_tests.py 
    def get_all_messages(self, person):
        """
        Retrieve all the messages waiting to be read. If there are no messages, return an empty list
        :param person: who received the messages (both direct and broadcast)
        :return: the list of messages ordered by arrival time and priority
        """

        reading_messages = []
        # loops for getting High and medium priority first and low
        for message in self.messages[person.get_person_id()]:
            if message.priority == Priority.HIGH:
                reading_messages.append(message)
        for message in self.messages[person.get_person_id()]:
            if message.priority == Priority.MEDIUM:
                reading_messages.append(message)
        for message in self.messages[person.get_person_id()]:
            if message.priority == Priority.LOW:
                reading_messages.append(message)
        # deleting messages from list as messages that are read hsort not be shown again
        self.delete_specific_messages(person)
        return reading_messages

    # Being checked in test_smoke_tests.py via getting_all_messages function
    def delete_specific_messages(self, person):
        # delete messages of a specific person
        self.messages[person.get_person_id()] = []


class CommunicationNetwork:
    def __init__(self):
        """
        Default initializer. The network contains nodes, links and the registry
        """
        self._registry = Registry()
        self.network = {} # For storing graph in adjacency list
        self.nodes = {} # For storing the nodes against their index
        self.node_index_list = [] # for storing index of the nodes
        self.persons = {} # For storing Persons

    # Being checked in test_smoke_tests.py
    # NOTE: REVIEWED `node_id` as a Node instance
    def add(self, node):
        """
        Add a new node to the network. Fail with an InvalidNetworkException if a node with the same node_id exists.
        :param node:
        :return:
        """
        # checking if nodes are in list
        if node.node_id in self.node_index_list:
            raise InvalidNetworkException("Node already exist in the network")
        # adding node to the network
        self.network[node.node_id] = [] 
        self.nodes[node.node_id] = node
        self.node_index_list.append(node.node_id)

    # Being checked in test_smoke_tests.py via delete remove function
    def check_nodes_reachable(self):
        """For checking if all nodes are reachable"""
        visited = []  # for checking if a node is visited or not
        if len(self.node_index_list) != 0:
            # calling recursive function that traverse avery node(DFS)
            CommunicationNetwork.check_node_at_index(self.network, visited, self.node_index_list[0])
            # if length is equal to len of nodes then it means all nodes are reachable
            if len(visited) != len(self.network):
                return False
        return True  
    
    # Helper function for checking - being chekced via check_nodes_reachable
    def check_node_at_index(graph, visited, index):
        if index in visited:
            return
        visited.append(index)
        # traversing neighbors nodes
        for node in graph[index]:
            CommunicationNetwork.check_node_at_index(graph, visited, node[0])

    # being checked in test_network.py
    def remove(self, node):
        """
        Remove the node with the given node_id from the network. Do nothing if the node does not exist.
        Disconnect all the persons that are attached to this node and discard any "unread" message.
        Fail with an InvalidNetworkException if the network becomes invalid after removing the node.
        :param node:
        :return:
        """
        if node.node_id not in self.node_index_list:
            raise InvalidNetworkException("Node not in the network")
        # traversing all nodes
        for key in self.network.keys():
            for tup in self.network[key]:
                # if node is in network
                if node.node_id == tup[0]:
                    self.network[key].remove(tup)
        # deleting from network
        del(self.network[node.node_id])
        del(self.nodes[node.node_id])
        self.node_index_list.remove(node.node_id)
        # checking if all of the nodes are reachable
        if self.check_nodes_reachable() == False:
            raise InvalidNetworkException("All nodes are not reachable!")


        
    # Being checked in test_smoke_tests.py
    def link(self, node_1, node_2, cost):
        """
        Connect the two nodes using an undirected/bi-directional link with a given cost.
        - Fail with an InvalidNetworkException if the nodes are the same (no self-loop)
        - Fail with an InvalidNetworkException if any of the nodes does not exist
        - Fail with an InvalidNetworkException if the nodes are already linked
        - Fail with an InvalidNetworkException if the cost is not positive
        :param node_1:
        :param node_2:
        :param cost: non-zero, positive value
        :return:
        """
        # checking different cases in which there should be exception
        if node_1.node_id == node_2.node_id:
            raise InvalidNetworkException("Same nodes!")
        if node_1.node_id not in self.node_index_list or node_2.node_id not in self.node_index_list:
            raise InvalidNetworkException("one of the node not exist")
        if (node_1.node_id, cost) in self.network[node_2.node_id]:
            raise InvalidNetworkException("Link already exists")
        if cost < 0 :
            raise InvalidNetworkException("Cost is negative")
        # finally appending it to the network
        self.network[node_1.node_id].append((node_2.node_id, cost))
        self.network[node_2.node_id].append((node_1.node_id, cost))
    
    # being checked in test_network.py
    def unlink(self, node_1, node_2):
        """
        Disconnect the two nodes. Do nothing if the nodes do not exist or are not connected
        :param node_1:
        :param node_2:
        :return:
        """
        # checking if these nodes exist 
        if node_1.node_id in self.node_index_list and node_2.node_id in self.node_index_list:
            # traversing network
            for tup in self.network[node_1.node_id]:
                if node_2.node_id == tup[0]:
                    # removing the link
                    self.network[node_1.node_id].remove(tup)
            for tup in self.network[node_2.node_id]:
                # removing the link
                if node_1.node_id == tup[0]:
                    self.network[node_2.node_id].remove(tup)

    # being checked in test_network.py
    def is_valid(self): 
        """
        Validate the network
        :return: True if the network is connected, i.e., each node is reachable from any other node (except itself)
        """
        return self.check_nodes_reachable()

    # Being checked in test_smoke_tests.py
    def broadcast(self, message):
        """
        Send the message from the sender to all connected recipients (but not the sender). Note: message.receiver must be None.
        - Fail if message.receiver is not None
        - Fail if message.sender is not registered in the network
        :param message: an object with sender, priority, content, and recipient fields.
        :return:
        """
        # checking the sender receiver is none
        if message.receiver is not None:
            raise Exception("Reciever is not none")
        # person is connected ?
        if self._registry.is_connected(message.sender) == False:
            raise Exception("Sender is not connected to network")
        # sending message to all nodes
        for node in self.node_index_list:
            # getting shortest path
            shortest_path = self.get_shortest_path(message,node)
            self.nodes[node].network = self # giving access to network for communication
            # actually sending the message
            self.nodes[node].receive(message)
            # forwarding the message one by one
            for i in range(len(shortest_path)):
                self.forward(message, int(shortest_path[i]))
            
    # Being checked in test_smoke_tests.py via get_short_path function
    def find_shortest_for_all(graph, vertex):
        visited = []    # for checking if purticular node is visited
        unvisited = list(graph.keys())
        short_cost_table = {}    # for storing low_cost_path
        for node in unvisited:
            # storing arbitrary infinity (9999999999) value at index
            # Dijkarstra Technique
            short_cost_table[node] = [999999999999, vertex]
        short_cost_table[vertex][0] = 0
        # calling recursive function for (DFS) on graph
        CommunicationNetwork.check_short_cost_at_index(graph, visited, unvisited, vertex, short_cost_table)
        return short_cost_table
    
    # Being checked in test_smoke_tests.py via send function
    def get_shortest_path(self, message, receiver):
        # getting sender node from registry
        sender_node = self._registry.get_node_id(message.sender)
        # using Dijkstra Algorithm
        shortest_path_table = CommunicationNetwork.find_shortest_for_all(self.network, sender_node)
        temp = receiver
        shortest_path = str(temp)
        while True:
            temp = shortest_path_table[temp][1]
            if temp == sender_node:
                break
            # saving shortes path from table to a string
            shortest_path += str(temp)
        shortest_path = shortest_path[::-1] # revesing the string
        return shortest_path

    # Being checked in test_smoke_tests.py via find_shortest_for_all function
    def check_short_cost_at_index(graph, visited, unvisited, vertex, short_cost_table):
        # base case for recursion
        if vertex in visited:
            return
        # adding to visited
        visited.append(vertex)
        unvisited.remove(vertex)
        # travesing neighbors nodes
        for node in graph[vertex]:
            # checking if cost is lower
            if node[1] + short_cost_table[vertex][0] < short_cost_table[node[0]][0]:
                short_cost_table[node[0]][0] = node[1] + short_cost_table[vertex][0]
                short_cost_table[node[0]][1] = vertex
            # if not visited then visiting it
            if node[0] not in visited:
                CommunicationNetwork.check_short_cost_at_index(graph, visited, unvisited, node[0], short_cost_table)
                visited.remove(node[0])
                unvisited.append(node[0])

    # Being checked in test_smoke_tests.py
    def send(self, message):
        """
        Send the message from the sender to the recipient specified inside the message (i.e., message.receiver)
        - Fail if message.receiver is not registered
        - Fail if message.sender is not registered in the network
        :param message: an object with sender, priority, content, and recipient fields
        :return:
        """
        # sender and recepient are connected?
        if self._registry.is_connected(message.sender) == False:
            raise Exception("Sender is not connected to network")
        if message.receiver is not None:
            if self._registry.is_connected(message.receiver) == False:
                raise Exception("Receiver is not connected to network")
            receiver_node = self._registry.get_node_id(message.receiver)
            shortest_path = self.get_shortest_path(message, receiver_node)
            # forwarding the message
            for i in range(len(shortest_path)):
                self.forward(message, self.nodes[int(shortest_path[i])])
            # actually sending the message
            self.nodes[receiver_node].receive(message)
            
    # being checked in test_smoke_tests.py via send and broadcast
    def forward(self, message, node):
        """
        Simulate the forward of the message to an (intermediate) node.
        :param message:
        :param node: node which the message is forwarded to
        :return:
        """
        # just for showing that the message is being forward using shortest path
        pass
    
    # being checked in test_smoke_tests.py
    def join_network(self, person, node_id):
        """
        Register the person in the network, including adding all the information to the Registry
        :param person: the person object that must be registered in the network at the given node
        :param node_id: the id of the node which will become the gateway for the person
        :return:
        """
        # adding to network
        self.persons[person.get_person_id()] = person
        # storing persons serailized key in registry
        self._registry.insert(person.get_person_id(), node_id, person.get_serialized_key())
        person.network = self # giving person the access to the network

    # being checked in test_network.py 
    def leave_network(self, person):
        """
        Remove this person and all the unread messages from the network and delete all the infos from the Registry
        :param person:
        :return:
        """
        # deleting person from the network persons
        del(self.persons[person.get_person_id()])
        # fetching node from the registry
        node_id = self._registry.get_node_id(person.get_person_id())
        # deleting messages from the node
        if node_id is not None:
            self.nodes[node_id].delete_specific_messages(person)
        else:
            raise RegistryException("Node not found")
        # deleting from the registry
        self._registry.delete(person.get_person_id())

    # being checked in test_smoke_tests.py and test_network.py
    def get_all_messages(self, person): 
        """
        Retrieve all the messages waiting to be read. If there are no messages, return an empty list
        :param person: who received the messages (both direct and broadcast)
        :return: the list of messages ordered by arrival time and priority
        """
        # fetching node from the registry
        node_id = self._registry.get_node_id(person.get_person_id())
        # getting messages of a person
        if node_id is not None:
            return self.nodes[node_id].get_all_messages(person)
        else:
            raise RegistryException("Node not found")