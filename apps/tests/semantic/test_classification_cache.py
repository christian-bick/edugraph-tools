import time

import pytest
from assertpy import assert_that

from semantic.classification_cache import ClassificationCache


class TestClassificationTest:

    @pytest.fixture
    def cache(self):
        return ClassificationCache(0.1)

    def test_update_get(self, cache):
        cache.update('test', {'x': 'y'})
        result = cache.get('test')
        assert_that(result).is_equal_to({'x': 'y'})

    def test_timeout(self, cache):
        cache.update('test', 'value')
        time.sleep(0.11)
        result = cache.get('test')
        assert_that(result).is_none()
