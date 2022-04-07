from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
from enum import Enum
from uuid import UUID
from pprint import pprint

from framework import settings


# persistent engines
class PersistenceEngineType(Enum):
    JSON = 1


# PersistenceEngine storage Interface class
class PersistenceEngine(ABC):

    # Get entity method, return stored data object; data object parameter needed to decode custom types
    @abstractmethod
    def get(self, element_id: UUID = None):
        pass

    # Set entity to data object method, return success status
    @abstractmethod
    def set(self, element) -> bool:
        pass

    @abstractmethod
    def delete(self, element) -> bool:
        pass

# data access configuration
@dataclass
class PersistenceDataConfig:
    engineType: PersistenceEngineType
    dataSource: str
    engine: PersistenceEngine


# Class holding PersistenceEngine objects for all registered classes
# Call register() to register a class,
# then call engine() to access the PersistenceEngine for this class and call its methods to get data
class Persistence:
    __classes = {}

    @staticmethod
    def register(class_to_register, engine_type: PersistenceEngineType, data_source: str) -> bool:
        # Get persistence engine instance
        if engine_type == PersistenceEngineType.JSON:
            engine = PersistenceJSON(data_source, class_to_register)
        else:
            return False  # fail if invalid engine type
        # Register persistent class in the dictionary
        Persistence.__classes[class_to_register] = PersistenceDataConfig(engine_type, data_source, engine)
        #pprint(Persistence.__classes)
        return True

    @staticmethod
    def engine(for_class):
        return Persistence.__classes[for_class].engine


# A custom class that has to be serialized to JSON by PersistenceJSON should inherit this class
class PersistenceSerializable(ABC):
    pass


# A specialized encoder that encodes custom classes inheriting from PersistenceSerializable to JSON
# Encoding is based on this idea: https://pythontic.com/serialization/json/introduction ,
#                                 https://pynative.com/make-python-class-json-serializable/
# Decoding is based on this idea: https://pynative.com/python-convert-json-data-into-custom-python-object/
# PARAM:
# classInitializer - initializer of the class to restore for custom_decoder ( custom_decoder_set_class() )
class PersistenceJSONCodec(json.JSONEncoder):

    # Override default() method from the default JSON encoder
    def default(self, data):
        if isinstance(data, UUID):          # Take care of UUIDs
            return data.hex
        elif isinstance(data, PersistenceSerializable):
            # return dictionary of parameters if the right class
            return data.__dict__
        else:
            # call the base class method to take care of raising exceptions for unsupported classes
            return super().default(data)

    # Set name of the class to restore for custom_decoder
    def custom_decoder_set_class(self, class_initializer):
        self.classInitializer = class_initializer

    # Decoder method for reading JSON
    def custom_decoder(self, generic_dict):
        #pprint(generic_dict)
        #dict_array = namedtuple(self.className, generic_dict.keys())(*generic_dict.values())
        instance = self.classInitializer(**generic_dict)
        return instance


# JSON persistence storage class
# PARAMS:
# jsonFile - JSON file full path (__init__())
# jsonClass - pathon Class name to correcty restore it from JSON file (__init__()
class PersistenceJSON(PersistenceEngine):
    error_object = None                     # Error object of the last unsuccessful operation
    error_message = ""                      # Error message of the last unsuccessful operation

    # JSON files directory path should be passed to data_source
    def __init__(self, data_source: str, class_initializer):
        self.jsonFile = data_source
        self.jsonClass = class_initializer

    # element_id - specify the required element id if you want to find specific record
    def get(self, element_id: UUID = None):
        # Open json file
        try:
            with open(self.jsonFile, 'r', encoding=settings.HTML_ENCODING) as f:
                # Read json file, converting names dictionary being read in the namespace of the destination object
                decoder = PersistenceJSONCodec()
                decoder.custom_decoder_set_class(self.jsonClass)
                array = json.load(f, object_hook=decoder.custom_decoder)
                # get element if requested
                if array and element_id:
                    array = [element for element in array if element.id == element_id]  # list of all elements this id
                # clear error objects
                self.error_object = None
                self.error_message = ""
                return array
        except FileNotFoundError as e:
            self.error_object = e
            self.error_message = "JSON file not found while performing get(): {}".format(self.jsonFile)
            # print(self.error_message)
            return []
        except json.JSONDecodeError as e:
            self.error_object = e
            self.error_message = "JSON decoder error in file: {}".format(self.jsonFile)
            # print(self.error_message)
            return []

    def _dump_array(self, array) -> bool:
        # Open json file
        try:
            with open(self.jsonFile, 'w', encoding=settings.HTML_ENCODING) as f:
                # Write json file, using custom JSON encoder for non-JSON-Serializable classes
                json.dump(array, f, indent=4, cls=PersistenceJSONCodec)
            return True
        except FileNotFoundError as e:
            self.error_object = e
            self.error_message = "JSON file not found while performing set(): {}".format(self.jsonFile)
            # self.print(self.error_message)
            return False

    def set(self, element) -> bool:
        # Get the existing data
        array = self.get()
        # Search for existing element
        if any([existing_element for existing_element in array if existing_element.id == element.id]):
            # Replace the changed element
            array = [element if existing_element.id == element.id else existing_element for existing_element in array]
        else:
            # Append the new element
            array.append(element)
        # Write results
        return self._dump_array(array)

    def delete(self, element) -> bool:
        # Get the existing data
        array = self.get()
        # Search for existing element
        existing_element = [existing_element for existing_element in array if existing_element.id == element.id]
        # Remove element with the specified id if found
        if existing_element and existing_element != []:
            # Delete the element
            array.remove(existing_element[0])
        # Write results
        return self._dump_array(array)
