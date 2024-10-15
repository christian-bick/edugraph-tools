from enum import Enum
from functools import reduce
from re import finditer


class OntologyUtil:

    def __init__(self, onto):
        self.onto = onto

    def entity_of_natural_name(self, value):
        classification_key = OntologyUtil.entity_name_of_natural_name(value)
        return getattr(self.onto, classification_key)

    def list_entities(self, entity_type):
        return list(self.onto.search(type=entity_type))

    def list_root_entities(self, entity_type):
        abilities = self.list_entities(entity_type)
        return list(filter(lambda entity: OntologyUtil.is_root_entity(entity), abilities))

    @staticmethod
    def __camel_case_split(identifier):
        matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
        return [m.group(0) for m in matches]

    @staticmethod
    def __list_as_words(list_of_words):
        return reduce(lambda a, b: a + ' ' +b, list_of_words).strip()

    @staticmethod
    def entity_name_of_natural_name(value):
        return value.replace(" ", "")

    @staticmethod
    def natural_name_of_entity(entity):
        name_list = OntologyUtil.__camel_case_split(entity.name)
        name_words = OntologyUtil.__list_as_words(name_list)
        return name_words

    @staticmethod
    def entities_as_enum(entities):
        skill_map = {entity.name: OntologyUtil.natural_name_of_entity(entity) for entity in entities}
        return Enum('SkillEnum', skill_map)

    @staticmethod
    def is_leaf_entity(entity):
        children = entity.INDIRECT_hasPart
        return children is None or len(children) == 0

    @staticmethod
    def is_root_entity(entity):
        parents = entity.INDIRECT_partOf
        return parents is None or len(parents) == 0