from semantic.ontology_util import OntologyUtil

def serialize_entity(entity):
    return {
        "name": entity.name,
        "natural_name": OntologyUtil.natural_name_of_entity(entity)
    }

def serialize_entity_tree(entities):
    def serialize_with_children(entity):
        serialized_entity = serialize_entity(entity)

        if not OntologyUtil.is_leaf_entity(entity):
            child_entities = entity.INDIRECT_hasPart
            serialized_children = serialize_entity_tree(child_entities)
            serialized_entity.update({
                "children": serialized_children
            })

        return serialized_entity

    serialized_entities = map(serialize_with_children, entities)
    return list(serialized_entities)
