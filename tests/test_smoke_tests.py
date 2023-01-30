#
# This class contains system, or end-to-end, tests
#
import string

# Make it possible to specificy a list of calls that are expected on the mock objects
from unittest.mock import call

from network import CommunicationNetwork, Node
from person import Person
from messaging import Key, Priority, Message


def test_communicate_over_simple_network():
    """
    Create a Simple network made of one node and register two users, alice and bob.
    Then Alice sends a message to Bob, and Bob reply to Alice.
    Note: this is a system test, so we do not make assertions for each of the operations.
    """
    cn: CommunicationNetwork[int] = CommunicationNetwork()
    node = Node(1)
    cn.add(node)

    # Create two users with their Keys
    # Training will skip the invalid chars (e.g., '.') and use the others to compute frequencies.
    alice = Person("alice", Key("this is a simple text to train create the key"))
    bob = Person(
        "bob",
        Key("this is another text. this is another text. this is another text. bob"),
    )

    # Register the users onto the CommunicationNetwork at the node, using the node_id
    cn.join_network(alice, node.node_id)
    cn.join_network(bob, node.node_id)

    # Alice sends messages to Bob. Note: . is not a valid character so we cannot put it into the message without causing an exception
    alice.send_message_to("bob", "hi bob")
    alice.send_message_to("bob", "meet me at 15")

    # Bob gets the messages and reply
    messages_to_bob = bob.get_all_messages()
    more_messages_to_bob = bob.get_all_messages()

    bob.send_message_to("alice", "at school")
    bob.send_urgent_message_to("alice", "sure meet me")
    bob.send_very_urgent_message_to("alice", "hi alice")

    # Alice gets the messages from Bob
    messages_to_alice = alice.get_all_messages()
    more_messages_to_alice = alice.get_all_messages()

    # Some assertions over the communication
    assert len(messages_to_bob) == 2
    assert len(more_messages_to_bob) == 0

    assert messages_to_bob[0].sender == "alice"
    assert messages_to_bob[0].content == "hi bob"
    assert messages_to_bob[0].priority == Priority.LOW
    # This is a direct message to from Alice to Bob
    assert messages_to_bob[0].receiver == "bob"

    assert messages_to_bob[1].sender == "alice"
    assert messages_to_bob[1].content == "meet me at 15"
    assert messages_to_bob[1].priority == Priority.LOW
    # This is a direct message to from Alice to Bob
    assert messages_to_bob[1].receiver == "bob"

    assert len(messages_to_alice) == 3
    assert len(more_messages_to_alice) == 0

    assert messages_to_alice[0].sender == "bob"
    assert messages_to_alice[0].priority == Priority.HIGH
    assert messages_to_alice[0].content == "hi alice"
    # This is a direct message to from Bob to Alice
    assert messages_to_alice[0].receiver == "alice"

    assert messages_to_alice[1].sender == "bob"
    assert messages_to_alice[1].priority == Priority.MEDIUM
    assert messages_to_alice[1].content == "sure meet me"
    # This is a direct message to from Bob to Alice
    assert messages_to_alice[1].receiver == "alice"

    assert messages_to_alice[2].sender == "bob"
    assert messages_to_alice[2].priority == Priority.LOW
    assert messages_to_alice[2].content == "at school"
    # This is a direct message to from Bob to Alice
    assert messages_to_alice[2].receiver == "alice"


def test_communicate_between_nodes():
    """
    Create a network made of two nodes and register four users, alice and bob on one node, carol and dave
    on the second node.

    Then alice sends broadcast messages and everybody receives it and reply to her

    Note: this is a system test, so we do not make assertions for each of the operations.
    """
    cn: CommunicationNetwork[int] = CommunicationNetwork()
    node_1 = Node(1)
    cn.add(node_1)
    node_2 = Node(2)
    cn.add(node_2)
    cn.link(node_1, node_2, 1)

    # Create the users with their Keys
    alice = Person("alice", Key("this is a simple text to train create the key"))
    bob = Person(
        "bob",
        Key("this is another text. this is another text. this is another text. bob"),
    )
    carol = Person("carol", Key("carol carol carol carol " + string.ascii_lowercase))
    dave = Person("dave", Key("dave dave dave daaaaaaaaavvvvveeeee"))

    # Register the users inside the CommunicationNetwork at nodes node_1 and node_2
    cn.join_network(alice, node_1.node_id)
    cn.join_network(bob, node_1.node_id)
    cn.join_network(carol, node_2.node_id)
    cn.join_network(dave, node_2.node_id)

    # Some messaging around = Note, it does it matter that one respond before getting the messages ;)
    alice.send_message_to_everyone("tonight party rsvp me")
    bob.send_message_to("alice", "sure i am in")
    dave.send_message_to("alice", "count me")
    carol.send_urgent_message_to_everyone("sorry cannot make it")

    # Read Messages
    messages_to_alice = alice.get_all_messages()
    messages_to_bob = bob.get_all_messages()
    messages_to_carol = carol.get_all_messages()
    messages_to_dave = dave.get_all_messages()

    # Re-send the message privately
    carol.send_message_to("alice", "sorry cannot make it")
    # Read More Messages
    more_messages_to_alice = alice.get_all_messages()

    # Assertions
    assert len(messages_to_alice) == 3
    # The first message is the one sent by carol to everybody since it has higher priority
    assert messages_to_alice[0].sender == "carol"
    assert messages_to_alice[0].content == "sorry cannot make it"
    assert messages_to_alice[0].priority == Priority.MEDIUM
    assert messages_to_alice[0].receiver is None

    # The second message is the one sent by bob directly to alice
    assert messages_to_alice[1].sender == "bob"
    assert messages_to_alice[1].content == "sure i am in"
    assert messages_to_alice[1].priority == Priority.LOW
    assert messages_to_alice[1].receiver == "alice"

    # The third message is the one sent by dave directly to alice
    assert messages_to_alice[2].sender == "dave"
    assert messages_to_alice[2].content == "count me"
    assert messages_to_alice[2].priority == Priority.LOW
    assert messages_to_alice[2].receiver == "alice"

    # The last message is the one sent again by carol directly to alice
    assert len(more_messages_to_alice) == 1
    assert more_messages_to_alice[0].sender == "carol"
    assert more_messages_to_alice[0].content == "sorry cannot make it"
    assert more_messages_to_alice[0].priority == Priority.LOW
    assert more_messages_to_alice[0].receiver == "alice"

    assert len(messages_to_bob) == 2
    # The first message is the one sent by carol to everybody since it has higher priority
    assert messages_to_bob[0].sender == "carol"
    assert messages_to_bob[0].content == "sorry cannot make it"
    assert messages_to_bob[0].priority == Priority.MEDIUM
    assert messages_to_bob[0].receiver is None

    # The second message is the one sent by alice to everybody
    assert messages_to_bob[1].sender == "alice"
    assert messages_to_bob[1].content == "tonight party rsvp me"
    assert messages_to_bob[1].priority == Priority.LOW
    assert messages_to_bob[1].receiver is None

    assert len(messages_to_dave) == 2

    # The first message is the one sent by carol to everybody since it has higher priority
    assert messages_to_dave[0].sender == "carol"
    assert messages_to_dave[0].content == "sorry cannot make it"
    assert messages_to_dave[0].priority == Priority.MEDIUM
    assert messages_to_dave[0].receiver is None

    # The second message is the one sent by alice to everybody
    assert messages_to_dave[1].sender == "alice"
    assert messages_to_dave[1].content == "tonight party rsvp me"
    assert messages_to_dave[1].priority == Priority.LOW
    assert messages_to_dave[1].receiver is None

    assert len(messages_to_carol) == 1

    #  The first message is the one sent by alice to everybody
    assert messages_to_carol[0].sender == "alice"
    assert messages_to_carol[0].content == "tonight party rsvp me"
    assert messages_to_carol[0].priority == Priority.LOW
    assert messages_to_carol[0].receiver is None


def test_sending_a_message_with_forwarding(mocker):

    """
    Create the network: node_1 --- node_2 --- node_3 -- node_4
    Send a message from node_1 to node_4 check that the message is
    - sent
    - forwarded
    - received
    correctly
    :return:
    """
    cn: CommunicationNetwork[int] = CommunicationNetwork()
    node_1 = Node(1)
    cn.add(node_1)
    node_2 = Node(2)
    cn.add(node_2)
    node_3 = Node(3)
    cn.add(node_3)
    node_4 = Node(4)
    cn.add(node_4)

    cn.link(node_1, node_2, 3)
    cn.link(node_2, node_3, 2)
    cn.link(node_3, node_4, 3)

    spy_send = mocker.spy(cn, "send")
    spy_forward = mocker.spy(cn, "forward")
    spy_receive = mocker.spy(node_4, "receive")
    # Mock an actual message to node 4
    alice = Person("alice", Key("This is Alice"))
    cn.join_network(alice, node_1.node_id)

    bob = Person("bob", Key("This is Bob"))
    cn.join_network(bob, node_4.node_id)

    alice.send_message_to("bob", "hi")

    # Send at node_1
    assert spy_send.call_count == 1
    # Forward at node_2
    # Forward at node_3
    # Forward at node_4
    assert spy_forward.call_count == 3
    # Received at node_4
    assert spy_receive.call_count == 1


def test_communicate_over_cheapest_path(mocker):
    """
        Create a network with three nodes and cycles, Alice and Bob joins on different nodes.
        Alice sends a message to Bob, and Bob reply to Alice, and the messages must follow the cheapest path
        Note: this is a system test, so we do not make assertions for each of the operations.

    :param mocker: this is a fixture provided by pytest (via pytest-mock) to spy on the objects.
    :return:
    """

    cn: CommunicationNetwork[int] = CommunicationNetwork()
    node_1 = Node(1)
    cn.add(node_1)
    node_2 = Node(2)
    cn.add(node_2)
    node_3 = Node(3)
    cn.add(node_3)

    cn.link(node_1, node_2, 1)
    cn.link(node_2, node_3, 2)
    cn.link(node_1, node_3, 10)

    # Create two users with their Keys
    alice = Person("alice", Key("this is a simple text to train create the key"))
    bob = Person(
        "bob",
        Key("this is another text. this is another text. this is another text. bob"),
    )

    # Register the users in the communicationNetwork at node
    cn.join_network(alice, node_1.node_id)
    cn.join_network(bob, node_3.node_id)

    # Setup the spy on the "forward" method of the communication network to check that the message is passed
    # along the cheapest path in this network between node 1 and node 3 (via node 2)
    spy_on_network = mocker.spy(cn, "forward")

    # Alice sends a direct message to bob
    alice.send_message_to("bob", "hi bob")

    # Check that the message is forwarded from the node_1 to the node_2 and from the node_2 to the node_3
    # So we EXPECT
    # 1) a call to cn.forward with second parameter node_2,
    # 2 followed by another call to cn.forward with second parameter node_3

    expected_sequence_of_forward_method_invocations = [call(mocker.ANY, node_2), call(mocker.ANY, node_3)]

    # Check that the forward method is invoked as expected
    spy_on_network.assert_has_calls(expected_sequence_of_forward_method_invocations)

    # bob gets the messages and reply
    messages_to_bob = bob.get_all_messages()
    bob.send_very_urgent_message_to("alice", "hi alice")

    # Check that the "reply" message is forwarded from the node_3 to the node_2 and from the node_2 to the node_1
    # So we EXPECT
    # 1) a call to cn.forward with second parameter node_2,
    # 2 followed by another call to cn.forward with second parameter node_1
    expected_sequence_of_forward_method_invocations = [call(mocker.ANY, node_2), call(mocker.ANY, node_1)]

    # Check that the forward method is invoked as expected
    spy_on_network.assert_has_calls(expected_sequence_of_forward_method_invocations)

    # alice gets the messages
    messages_to_alice = alice.get_all_messages()

    # Assertions
    assert len(messages_to_alice) == 1
    assert messages_to_alice[0].sender == "bob"
    assert messages_to_alice[0].content == "hi alice"
    assert messages_to_alice[0].priority == Priority.HIGH

    assert len(messages_to_bob) == 1
    assert messages_to_bob[0].sender == "alice"
    assert messages_to_bob[0].content == "hi bob"
    assert messages_to_bob[0].priority == Priority.LOW
