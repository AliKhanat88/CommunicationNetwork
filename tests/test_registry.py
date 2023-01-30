import pytest

from network import Node, CommunicationNetwork, InvalidNetworkException
from person import Person
from messaging import Key
from registry import Registry, RegistryException


def test_registry():
    """
    Create a valid network, then remove a node that makes it invalid, expect an InvalidNetworkException
    :return:
    """
    reg = Registry()
    
    alice = Person("alice", Key("this is a simple text to train create the key"))
    bob = Person(
        "bob",
        Key("this is another text. this is another text. this is another text. bob"),
    )

    reg.insert(bob._id, 1, "saldmsla")

    assert reg.is_connected(bob._id)

    reg.delete(bob._id)

    assert reg.is_connected(bob._id) == False

    assert reg.get_serialized_key(alice._id) is None

    assert reg.get_node_id(alice._key) is None
    
    reg.insert(bob._id, 1, "saldmsla")
    
    with pytest.raises(RegistryException):
        reg.insert(bob._id, 1, "saldmsla")

