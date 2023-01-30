import pytest

from network import Node, CommunicationNetwork, InvalidNetworkException
from person import Person
from messaging import Key, Priority

def test_person():
    cn: CommunicationNetwork[int] = CommunicationNetwork()
    node_1 = Node(1)
    cn.add(node_1)
    node_2 = Node(2)
    cn.add(node_2)
    cn.link(node_1, node_2, 1)

    # Create the users with their Keys
    alice = Person("alice", Key("this is a simple text to train create the key"))
    dave = Person("dave", Key("dave dave dave daaaaaaaaavvvvveeeee"))

    # Register the users inside the CommunicationNetwork at nodes node_1 and node_2
    cn.join_network(alice, node_1.node_id)
    cn.join_network(dave, node_2.node_id)

    # Some messaging around = Note, it does it matter that one respond before getting the messages ;)
    alice.send_message_to_everyone("tonight party rsvp me")
    dave.send_message_to("alice", "count me")

    # Read Messages
    messages_to_alice = alice.get_all_messages()

    # Re-send the message privately
    dave.send_message_to("alice", "sorry cannot make it")
    # Read More Messages
    more_messages_to_alice = alice.get_all_messages()

    # Assertions
    assert len(messages_to_alice) == 1
    # The first message is the one sent by carol to everybody since it has higher priority
    assert messages_to_alice[0].sender == "dave"
    assert messages_to_alice[0].content == "count me"
    assert messages_to_alice[0].priority == Priority.LOW
    assert messages_to_alice[0].receiver == "alice"

    dave.send_urgent_message_to("alice", "hey wattsapp")
    dave.send_very_urgent_message_to("alice", "hey wattsapp")
    dave.send_message_to("alice", "asd askdnkajsd")
    dave.send_message_to_everyone("asfnsdk")

    dave.send_very_urgent_message_to_everyone("sdadas")
    dave.send_urgent_message_to_everyone("dsaasdas")
    
    alice_messages = alice.get_all_messages()
test_person()