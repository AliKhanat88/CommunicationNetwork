from enum import IntEnum
from collections import defaultdict

# Enum class for the Priority of the message
class Priority(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
# More code combination to bind them with the key
class Morse_code:
    combinations = [
        ".",
        "-",
        "..",
        ".-",
        "-.",
        "--",
        "...",
        "..-", 
        ".-.", 
        ".--",
        "-..", 
        "-.-", 
        "--.", 
        "---",
        "....", 
        "...-", 
        "..-.", 
        "..--", 
        ".-..",
        ".-.-",
        ".--.",
        ".---", 
        "-...", 
        "-..-", 
        "-.-.",
        "-.--",
        "--..", 
        "--.-", 
        "---.", 
        "----",
        "....."
        "....-",
        "...-.",
        "...--",
        "..-..",
        "..-.-"
    ]

# Will contain every exception related to Content and key
class InvalidContentException(Exception):
    """
    A generic exception for problems in the message
    """

    pass


class Key:
    """
    The encoding/deconding key to transform a plain text into a sequence of '.' (dot), '-' (line), ' ' (space),
    '/' (word separator).
    """

    def __init__(self, training_text):
        """
        Default initializer. Given the training text build the internal structure of the key
        :param training_text:
        """
        # for calculating frequencies of chars
        frequencies = defaultdict(int)
        for word_chr in training_text:
            # if word is other than defined chars like . , 
            if ord(word_chr) >= ord("a") and ord(word_chr) <= ord("z") or ord(word_chr) >= ord("0") and ord(word_chr) <= ord("9"):
                frequencies[word_chr] += 1
        # for maminf key
        keys = list(frequencies.keys())
        values = list(frequencies.values())
        # sorting in desending order so that low chars are used for less dots and slashes
        for i in range(len(values) -1):
            for j in range(len(values) -1):
                if values[j] < values[j+1]:
                    values[j], values[j+1] = values[j+1], values[j]
                    keys[j], keys[j+1] = keys[j+1], keys[j]
        # for storing chars whose frequency is 0
        for i in range(ord("a"), ord("z")+1):
            if chr(i) not in keys:
                keys.append(chr(i))
        # for storing numbers whose frequency is 0
        for i in range(ord("0"), ord("9")+1):
            if chr(i) not in keys:
                keys.append(chr(i))
        self.key = keys


    @classmethod
    def serialize(cls, the_key):
        """
        Serialize the given key into a string to be stored in the registry
        :param the_key: the actual key object
        :return: a string corresponding to the key
        """
        # just converting it in string to be saved in registry
        return "".join(the_key.key)

    @classmethod
    def deserialize(cls, the_serialized_key):
        """
        Rebuild the key from a the input string read from the registry
        :param the_serialized_key: a string corresponding to the key
        :return: the actual key object
        """
        # converting it back from string to list
        return list(the_serialized_key)

    def encode(self, plain_content):
        """
        Encode the content using the key.
        - Fails with an InvalidContentException if the plain content contains unsupported chars
        :param plain_content:
        :return: encoded_content: made only using the symbols: '.', '-', ' ', '/'
        """
        encoded_string = ""
        for word_chr in plain_content:
            # checking for space
            if word_chr == " ":
                encoded_string += "/ "
            else:
                if word_chr not in self.key:
                    raise InvalidContentException("Got an invalid chracter!")
                # checking its index in key
                index = self.key.index(word_chr)
                # reading its value in morse code from same index
                encoded_string += Morse_code.combinations[index] + " "
        # returning without space at the last
        return encoded_string[0:-1]

    def decode(self, encoded_content):
        """
        Decode the content using the key.
        - Fails with an InvalidContentException if the encoded content contains unsupported chars
        :param encoded_content:
        :return: decoded_content, i.e., plain content
        """
        # as space seprated so I split on spaces
        list_encoded_string = encoded_content.split()
        decoded_string = ""
        for word_chr in list_encoded_string:
            # checking for space
            if word_chr == "/":
                decoded_string += " "
            else:
                if word_chr not in Morse_code.combinations:
                    raise InvalidContentException("Invalid chr in encoded string")
                else:
                    # checking index in morse code
                    index = Morse_code.combinations.index(word_chr)
                    # storing char from same index in key
                    decoded_string += self.key[index]
        return decoded_string



class Message:
    """
    A data object containing the relevant information for an message
    """

    def __init__(self, from_person_id, content, priority, to_person_id=None):
        """
        :param from_person_id: id of the person
        :param content: content of the message
        :param priority: one of Priority enumeratoin
        :param to_person_id: id of the receiver. This can be None only for broadcasted messages
        """
        # just assigning data members
        self.sender = from_person_id
        self.content = content
        self.priority = priority
        self.receiver = to_person_id