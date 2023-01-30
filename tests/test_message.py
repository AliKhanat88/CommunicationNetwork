import pytest

from network import Node, CommunicationNetwork, InvalidNetworkException
from person import Person
from messaging import Key, InvalidContentException
from registry import Registry


def test_message():
    """
    Create a valid network, then remove a node that makes it invalid, expect an InvalidNetworkException
    :return:
    """
    key = Key("aaaaaaaaaaaaadsdsndks") # training text
    
    text = "i am here"
    encoding = key.encode(text)
    decoding = key.decode(encoding)

    assert decoding == text

    # checking the "." is used for most frequent
    assert key.key[0] == "a"

    with pytest.raises(InvalidContentException):
        key.encode("asdklasA")

    with pytest.raises(InvalidContentException):
        key.decode("........")
