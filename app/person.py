from messaging import Key, Message, Priority
import copy

class Person:
    def __init__(self, person_id, encoding_key):
        """
        Default initializer. Add explicit setters/getters if you need to initialize attributes.
        :param person_id: the unique id of this person
        :param encoding_key: the "trained" key used for encoding and decoding the messages
        """
        self._id = person_id
        self._key = encoding_key

    # simple getter for person_id
    def get_person_id(self):
        return self._id

    
    def get_serialized_key(self):
        """
        The encoding/decoding key can be stored inside the Registry ONLY if serialized to a stream of bytes, values, etc...
        :return:
        """
        # just for convering the key in string - calling key's serialize function 
        return Key.serialize(self._key)

    def send_message_to(self, to_person_id, plain_content):
        """
        Send a message with LOW priority to another person.
        :param to_person_id: the id of the receiver person
        :param plain_content: the content of the message that must be encoded before
        :return:
        dcjknnin i also  cano cano  sfjjjknfi  akniofao  adopen adiffka jnconias to ask for help i dont know ehwta im doing wrifvjkak
        dbancieo
         alsoo fast API
        """
        # encoding 
        encoded_text = self._key.encode(plain_content)
        message = Message(self.get_person_id(), encoded_text, Priority.LOW, to_person_id)
        self.network.send(message)



    def send_urgent_message_to(self, to_person_id, plain_content):
        """
        Send a message with MEDIUM priority to another person.
        :param to_person_id: the id of the receiver person
        :param plain_content: the content of the message that must be encoded before
        :return:
        """
        encoded_text = self._key.encode(plain_content)
        message = Message(self.get_person_id(), encoded_text, Priority.MEDIUM, to_person_id)
        # using network to send message
        self.network.send(message)

    def send_very_urgent_message_to(self, to_person_id, plain_content):
        """
        Send a message with HIGH priority to another person.
        :param to_person_id: the id of the receiver person
        :param plain_content: the content of the message that must be encoded before
        :return:
        """
        encoded_text = self._key.encode(plain_content)
        message = Message(self.get_person_id(), encoded_text, Priority.HIGH, to_person_id)
        # using network to send message
        self.network.send(message)

    def send_message_to_everyone(self, plain_content):
        """
        Send a LOW priority broadcast message
        :param plain_content: the content of the message that must be encoded before
        :return:
        """
        encoded_text = self._key.encode(plain_content)
        # same but none is used and same for next two functions
        message = Message(self.get_person_id(), encoded_text, Priority.LOW, None)
        # using network to send message
        self.network.broadcast(message)

    def send_urgent_message_to_everyone(self, plain_content):
        """
        Send a MEDIUM priority broadcast message
        :param plain_content: the content of the message that must be encoded before
        :return:
        """
        encoded_text = self._key.encode(plain_content)
        message = Message(self.get_person_id(), encoded_text, Priority.MEDIUM, None)
        # using network to send message
        self.network.broadcast(message)

    def send_very_urgent_message_to_everyone(self, plain_content):
        """
        Send a HIGH priority broadcast message
        :param plain_content: the content of the message that must be encoded before
        :return:
        """
        encoded_text = self._key.encode(plain_content)
        message = Message(self.get_person_id(), encoded_text, Priority.HIGH, None)
        # using network to send message
        self.network.broadcast(message)

    def get_all_messages(self):
        """
        Retrieve all the messages waiting to be read. If there are no messages, return an empty list
        :return: the ORDERED list of message or an empty list. The order is defined by priority and the time at which
            messages were received
        """
        # using network to get node and node_id
        node_id = self.network._registry.get_node_id(self._id)
        # getting all messages from node
        node = self.network.nodes[node_id]
        encoded_messages = node.get_all_messages(self)
        decoded_messages = []
        # decoding the messages
        for message in encoded_messages:
            # Getting sender's key from registry
            sender_key = self.network._registry.get_serialized_key(message.sender)
            sender_key = Key.deserialize(sender_key)
            # making a dummy object of key
            key_object_sender = Key("abc")
            key_object_sender.key = sender_key
            # making copy of message so it is not changed for other readers
            temp_message = copy.deepcopy(message)
            temp_message.content = key_object_sender.decode(message.content)
            # decoding and storing 
            decoded_messages.append(temp_message)
        return decoded_messages
        