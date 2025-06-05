from semantic.ontology_util import *


def serialize_entity(entity):
    return {
        "name": entity.name,
        "natural_name": natural_name_of_entity(entity)
    }


def serialize_entity_with_name(entity_name):
    return {
        "name": entity_name,
        "natural_name": natural_name_of_entity_name(entity_name)
    }


def serialize_entities_with_names(entity_name_list):
    return [serialize_entity_with_name(name) for name in entity_name_list]


def serialize_entity_tree(entities, relationName):
    def serialize_with_children(entity):
        serialized_entity = serialize_entity(entity)

        children = []
        if hasattr(entity, relationName):
            children = getattr(entity, relationName)

        if len(children) > 0:
            serialized_entity.update({
                "children": serialize_entity_tree(children, relationName)
            })

        return serialized_entity

    serialized_entities = map(serialize_with_children, entities)
    return list(serialized_entities)


def get_related_entities(entity, relationName):
    related_entities = []
    if hasattr(entity, relationName):
        related_entities = getattr(entity, relationName)
    return related_entities


def get_parent_related_entities(entity, relationName, parentRelationName):
    parents = get_related_entities(entity, parentRelationName)
    related_entities = []
    for parent in parents:
        related_entities += get_related_entities(parent, relationName)
        related_entities += get_parent_related_entities(parent, relationName, parentRelationName)
    return related_entities


def serialize_entity_tree_with_parent_relations(entities, relationName, parentRelationName):
    def serialize_with_children(entity):
        serialized_entity = serialize_entity(entity)

        related_entities = get_related_entities(entity, relationName)
        related_entities += get_parent_related_entities(entity, relationName, parentRelationName)

        if len(related_entities) > 0:
            serialized_entity.update({
                "children": serialize_entity_tree(related_entities, relationName)
            })

        return serialized_entity

    serialized_entities = map(serialize_with_children, entities)
    return list(serialized_entities)
