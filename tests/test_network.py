import pytest

from network import Node, CommunicationNetwork, InvalidNetworkException
from person import Person
from messaging import Key, Priority, Message

def test_removing_not_fails_if_invalid():
    """
    Create a valid network, then remove a node that makes it invalid, expect an InvalidNetworkException
    :return:
    """
    cn: CommunicationNetwork[int] = CommunicationNetwork()
    node_1 = Node(1)
    node_2 = Node(2)
    node_3 = Node(3)

    # Add the nodes to the network so they can be linked together
    cn.add(node_1)
    cn.add(node_2)
    cn.add(node_3)

    cn.link(node_1, node_2, 2)
    cn.link(node_2, node_3, 3)

    alice = Person("alice", Key("this is a simple text to train create the key"))
    dave = Person("dave", Key("dave dave dave daaaaaaaaavvvvveeeee"))

    # node_1 --- node_2 --- node_3
    assert cn.is_valid()

    with pytest.raises(InvalidNetworkException):
        cn.remove(node_2)

    # msg = Message(alice._id, "asdasd", Priority.LOW, None)

    # node_1.receive(msg)
    node_2 = Node(2)

    # Add the nodes to the network so they can be linked together
    cn.add(node_2)

    cn.link(node_1, node_2, 2)
    cn.link(node_2, node_3, 3)
    
    abc = Person("abc", Key("sakdnlkasnd"))
    cn.join_network(abc, node_2.node_id)
    cn.join_network(alice, node_1.node_id)
    cn.join_network(dave, node_2.node_id)
    alice.send_message_to_everyone("safafasfas")
    with pytest.raises(InvalidNetworkException):
        cn.add(node_2)

    node_4 = Node(4)
    cn.add(node_4)
    cn.remove(node_4)

    with pytest.raises(InvalidNetworkException):
        cn.remove(node_4)

    with pytest.raises(InvalidNetworkException):
        cn.link(node_1, node_2, -2)

    with pytest.raises(InvalidNetworkException):
        cn.link(node_1, node_1, 2)

    with pytest.raises(InvalidNetworkException):
        cn.link(node_4, node_1, 5)

    with pytest.raises(InvalidNetworkException):
        cn.link(node_1, node_2, 2)
    cn.unlink(node_1, node_2)

    message = Message("alice", "sdasd", Priority.LOW, "abc")
    
    with pytest.raises(Exception):
        cn.broadcast(message)

    message.sender = "asas"
    message.receiver = None
    with pytest.raises(Exception):
        cn.broadcast(message)

    message = Message("abcsd", "sdasd", Priority.LOW, "abc")
    
    with pytest.raises(Exception):
        cn.send(message)

    message.sender = "abc"
    message.receiver = "dasnak"
    with pytest.raises(Exception):
        cn.send(message)

    cn.leave_network(abc)

    messeges = cn.get_all_messages(alice)

    
test_removing_not_fails_if_invalid()
