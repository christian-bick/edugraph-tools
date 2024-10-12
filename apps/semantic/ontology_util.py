from collections import defaultdict
from enum import Enum
from functools import reduce
from re import finditer

class OntologyUtil:

    def __init__(self, onto):
        self.onto = onto

    def node_of_natural_name(self, value):
        classification_key = value.replace(" ", "")
        return getattr(self.onto, classification_key)

    @staticmethod
    def __camel_case_split(identifier):
        matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
        return [m.group(0) for m in matches]

    @staticmethod
    def __list_as_words(list_of_words):
        return reduce(lambda a, b: a + ' ' +b, list_of_words).strip()

    @staticmethod
    def entity_native_name(entity):
        name_list = OntologyUtil.__camel_case_split(entity.name)
        name_words = OntologyUtil.__list_as_words(name_list)
        return name_words

    @staticmethod
    def entities_as_enum(entities):
        skill_map = {entity.name: OntologyUtil.entity_native_name(entity) for entity in entities}
        return Enum('SkillEnum', skill_map)

    @staticmethod
    def is_leaf_entity(entity):
        children = entity.INDIRECT_hasPart
        return not (isinstance(children, list) and len(children) > 0)

    @staticmethod
    def collect_entity_leafs(entity):
        if OntologyUtil.is_leaf_entity(entity):
            return [entity]

        descriptor_parts = entity.INDIRECT_hasPart
        leafs = reduce(lambda tail, head: OntologyUtil.collect_entity_leafs(head) + tail, descriptor_parts, [])
        return leafs

    @staticmethod
    def cluster_entities_by_parent(entity):
        clusters = defaultdict(list)
        for entity in entity:
            parent_node = entity.INDIRECT_partOf[0]
            key = parent_node.name
            clusters[key].append(entity)
        return clusters

    @staticmethod
    def list_entities_parents(entities):
        leaf_parents = {}
        for entity in entities:
            parent_node = entity.INDIRECT_partOf[0]
            key = parent_node.name
            leaf_parents[key] = parent_node
        return leaf_parents.values()