import pytest

from semantic.classifiers.context_builder import *
from tests.entity_mock import EntityMock

expected_outline = (
"""1 e1
1.1 e1-e1
1.1.1 e1-e1-e1
1.1.2 e1-e1-e2
1.2 e1-e2
"""
)

expected_definitions = (
"""1 e1

e1-def

1.1 e1-e1

e1-e1-def

1.1.1 e1-e1-e1

e1-e1-e1-def

1.1.2 e1-e1-e2

e1-e1-e2-def

1.2 e1-e2

e1-e2-def

"""
)

expected_taxonomy = (
"""Taxonomy of Areas

A) Outline of Areas

{0}

B) Definitions of Areas

{1}"""
).format(expected_outline, expected_definitions)


class TestContextBuilders:

    @pytest.fixture
    def entities(self):
        return [EntityMock('e1', [
            EntityMock('e1-e1', [
                EntityMock('e1-e1-e1'),
                EntityMock('e1-e1-e2')
            ]), EntityMock(
                'e1-e2'
            )]
                           )]

    def test_build_outline(self, entities):
        outline = build_outline([1], entities)
        assert outline == expected_outline

    def test_build_definitions(self, entities):
        outline = build_definitions([1], entities)
        print(outline)
        print("-------")
        print(expected_definitions)
        assert outline == expected_definitions

    def test_build_taxonomy(self, entities):
        taxonomy = build_taxonomy('Areas', entities)
        assert taxonomy == expected_taxonomy
