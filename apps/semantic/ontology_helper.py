from collections import defaultdict
from enum import Enum
from functools import reduce
from re import finditer

class OntologyHelper:

    def __init__(self, onto):
        self.onto = onto

    @staticmethod
    def camel_case_split(identifier):
        matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
        return [m.group(0) for m in matches]

    @staticmethod
    def list_as_words(list):
        return reduce(lambda a, b: a + ' ' +b, list).strip()

    @staticmethod
    def id_as_name(name):
        name_list = OntologyHelper.camel_case_split(name)
        name_words = OntologyHelper.list_as_words(name_list)
        return name_words

    @staticmethod
    def entities_as_enum(entities):
        skill_map = {entity.name: OntologyHelper.id_as_name(entity.name) for entity in entities}
        return Enum('SkillEnum', skill_map)

    @staticmethod
    def is_leaf_entity(node):
        children = node.INDIRECT_hasPart
        return not (isinstance(children, list) and len(children) > 0)

    def node_of_value(self, value):
        classification_key = value.replace(" ", "")
        return getattr(self.onto, classification_key)

    @staticmethod
    def collect_leafs(descriptor_node):
        if OntologyHelper.is_leaf_entity(descriptor_node):
            return [ descriptor_node ]


        descriptor_parts = descriptor_node.INDIRECT_hasPart
        leafs = reduce(lambda tail, head: OntologyHelper.collect_leafs(head) + tail, descriptor_parts, [])
        return leafs

    @staticmethod
    def cluster_nodes(nodes):
        clusters = defaultdict(list)
        for node in nodes:
            parent_node = node.INDIRECT_partOf[0]
            key = parent_node.name
            clusters[key].append(node)
        return clusters

    @staticmethod
    def list_parents(nodes):
        leaf_parents = {}
        for node in nodes:
            parent_node = node.INDIRECT_partOf[0]
            key = parent_node.name
            leaf_parents[key] = parent_node
        return leaf_parents.values()