from functools import reduce

from semantic.ontology_util import OntologyUtil

taxonomy_header_template = "Taxonomy of {0}\n\n"
outline_header_template = "\nA) {0} Outline\n\n"
definition_header_template = "\nB) {0} Definitions\n\n"

class ContextBuilder:

    def __init__(self):
        self.context = None

    def add_taxonomy_header(self, name):
        self.context += "Taxonomy of {0}\n\n".format(name)

    def add_outline_header(self, name):
        self.context += "\n\nA) {0} Outline\n\n".format(name)

    def add_definition_header(self, name):
        self.context += "\n\nB) {0} Definitions\n\n".format(name)

    def build_area_context(self, nodes):
        name = "Area"
        self.context = ""
        self.add_taxonomy_header(name)
        self.add_outline_header(name)
        self.add_outline_context_rec([1], nodes)
        self.add_definition_header(name)
        self.add_definition_context_rec([1], nodes)
        return self.context

    def build_ability_context(self, nodes):
        name = "Ability"
        self.context = ""
        self.add_taxonomy_header(name)
        self.add_outline_header(name)
        self.add_outline_context_rec([1], nodes)
        self.add_definition_header(name)
        self.add_definition_context_rec([1], nodes)
        return self.context

    def build_scope_context(self, nodes):
        name = "Scope"
        self.context = ""
        self.add_taxonomy_header(name)
        self.add_outline_header(name)
        self.add_outline_context_rec([1], nodes)
        self.add_definition_header(name)
        self.add_definition_context_rec([1], nodes)
        return self.context

    def add_definition_context(self, hierarchy, node):

        definition = node.isDefinedBy

        if isinstance(definition, list) and len(definition) > 0:
            self.add_index_context(hierarchy, node)
            self.context += "\n{0}\n\n".format(definition[0])

    def add_definition_context_rec(self, hierarchy, nodes):
        current_index = len(hierarchy)-1
        current_counter = 1

        for node in nodes:
            hierarchy[current_index] = current_counter
            self.add_definition_context(hierarchy, node)

            if not OntologyUtil.is_leaf_entity(node):
                descriptor_parts = node.INDIRECT_hasPart
                new_hierarchy = hierarchy + [1]
                self.add_definition_context_rec(new_hierarchy, descriptor_parts)

            current_counter = current_counter + 1

    def add_index_context(self, hierarchy, node):
        hierarchy_as_string = (
            ContextBuilder.hierarchy_to_string(hierarchy) + ' ' + OntologyUtil.natural_name_of_entity(node) + '\n'
        )
        self.context += hierarchy_as_string

    def add_outline_context_rec(self, hierarchy, nodes):
        current_index = len(hierarchy)-1
        current_counter = 1

        for node in nodes:
            hierarchy[current_index] = current_counter
            self.add_index_context(hierarchy, node)

            if not OntologyUtil.is_leaf_entity(node):
                descriptor_parts = node.INDIRECT_hasPart
                new_hierarchy = hierarchy + [1]
                self.add_outline_context_rec(new_hierarchy, descriptor_parts)

            current_counter = current_counter + 1

    @staticmethod
    def hierarchy_to_string(hierarchy):
        level_string = reduce(lambda tail, head: tail + str(head) + '.', hierarchy, "")
        return level_string[:-1]