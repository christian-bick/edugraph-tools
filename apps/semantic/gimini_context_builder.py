from functools import reduce

from semantic.ontology_helper import OntologyHelper

class ContextBuilder:

    def __init__(self):
        self.context = None

    def build_area_context(self, nodes):
        hierarchy = [1]
        self.context = "Taxonomy of Areas\n\n"
        self.expand_index_context_rec(hierarchy, nodes)
        self.expand_definition_context_rec(hierarchy, nodes)
        return self.context

    def build_ability_context(self, nodes):
        hierarchy = [1]
        self.context = "Taxonomy of Abilities\n\n"
        self.expand_index_context_rec(hierarchy, nodes)
        self.expand_definition_context_rec(hierarchy, nodes)
        return self.context

    def build_scope_context(self, nodes):
        hierarchy = [1]
        self.context = "Taxonomy of Scopes\n\n"
        self.expand_index_context_rec(hierarchy, nodes)
        self.expand_definition_context_rec(hierarchy, nodes)
        return self.context

    def expand_definition_context(self, hierarchy, node):

        definition = node.isDefinedBy

        if isinstance(definition, list) and len(definition) > 0:
            self.expand_index_context(hierarchy, node)
            self.context += "\n{0}\n\n".format(definition[0])

    def expand_definition_context_rec(self, hierarchy, nodes):
        current_index = len(hierarchy)-1
        current_counter = 1

        for node in nodes:
            hierarchy[current_index] = current_counter
            self.expand_definition_context(hierarchy, node)

            if not OntologyHelper.is_leaf_entity(node):
                descriptor_parts = node.INDIRECT_hasPart
                new_hierarchy = hierarchy + [1]
                self.expand_definition_context_rec(new_hierarchy, descriptor_parts)

            current_counter = current_counter + 1

    def expand_index_context(self, hierarchy, node):
        hierarchy_as_string = (
            ContextBuilder.hierarchy_to_string(hierarchy) + ' ' + OntologyHelper.id_as_name(node.name) + '\n'
        )
        self.context += hierarchy_as_string

    def expand_index_context_rec(self, hierarchy, nodes):
        current_index = len(hierarchy)-1
        current_counter = 1

        for node in nodes:
            hierarchy[current_index] = current_counter
            self.expand_index_context(hierarchy, node)

            if not OntologyHelper.is_leaf_entity(node):
                descriptor_parts = node.INDIRECT_hasPart
                new_hierarchy = hierarchy + [1]
                self.expand_index_context_rec(new_hierarchy, descriptor_parts)

            current_counter = current_counter + 1

    @staticmethod
    def hierarchy_to_string(hierarchy):
        level_string = reduce(lambda tail, head: tail + str(head) + '.', hierarchy, "")
        return level_string[:-1]