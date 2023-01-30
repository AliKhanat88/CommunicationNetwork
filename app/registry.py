from collections import defaultdict

# for every exceptions regarding registry
class RegistryException(Exception):
    """
    A generic exception for problems in the registry
    """

    pass


class Registry:
    """
    This class implements a simple (in-memory) database that stores information about the Persons that have
    joined the network
    """

    def __init__(self):
        """
        Default constructor. Use explicit setters/getters to add more attributes
        """
        self.database = defaultdict(lambda:[])  # node_id -> key and the list of persons -> value
        self.persons = {}   # person_id -> serialized key
    
    # getter for serialized key being checked in test_smoke_tests.py via person.py
    def get_serialized_key(self, person_id):
        """
        Retrieve encoding/decoding key
        :param person_id:
        :return: the serialized key associated to the give person_id if exists otherwise return None
        """
        # Checking if person exists
        if person_id in self.persons.keys():
            return self.persons[person_id]
        return None   # if not then none

    # being checked by test_smoke_tests.py via network.py file
    def get_node_id(self, person_id):
        """
        Retrieve gateway node
        :param person_id:
        :return: the node_id associated to the give person_id if exists otherwise return None
        """
        # checking person in database and if exist then return it
        for key in self.database.keys():
            if person_id in self.database[key]:
                return key
        return None

    # being checked in test_registry.py
    def is_connected(self, person_id):
        """
        Check whether the person with the given id is connected to the network
        :param person_id:
        :return: True if the person is connected, False otherwise
        """
        for key in self.database.keys():
            if person_id in self.database[key]:
                return True
        return False

    # being checked in test_network.py via leave network function of network
    def delete(self, person_id):
        """
        Delete all the information associated to the person if the person exists. Do nothing otherwise
        :param person_id:
        :return:
        """
        # removing person from network
        for key in self.database.keys():
            if person_id in self.database[key]:
                self.database[key].remove(person_id)
        # also deleting its serailized key
        del(self.persons[person_id])

    # being checked in test_registry.py
    def insert(self, person_id, node_id, serialized_key):
        """
        Insert the information of a person joining the network
        - Fails with a RegistryException if a person with same id is already registered
        Note: The registry cannot store structured data, i.e., objects, so we need to provide only plain strings
        so they can be copied by value
        :param person_id: the id of the person
        :param node_id: the id of the node
        :param serialized_key: the serialized encoding/decoding key (this is a string!)
        :return:
        """
        # checking if person is against any node?
        for key in self.database.keys():
            if person_id in self.database[key]:
                raise RegistryException("Person Already exists!")
        # adding person to the registry against a purticular node
        if node_id in self.database.keys():
            self.database[node_id].append(person_id)
        else:
            self.database[node_id] = [person_id]
        self.persons[person_id] = serialized_key # also its serailized key