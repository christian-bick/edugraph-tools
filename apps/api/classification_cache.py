import time

ONE_HOUR = 60 * 60.0


class ClassificationCache:

    def __init__(self, expires=ONE_HOUR):
        self.cached_results = {}
        self.expires = expires

    def get(self, key):
        if key in self.cached_results:
            timestamp, value = self.cached_results[key]
            if time.time() - timestamp < self.expires:
                return value
            else:
                del self.cached_results[key]  # Remove expired entry
        return None

    def update(self, key, value):
        self.cached_results[key] = (time.time(), value)

    def timeout(self, key):
        self.cached_results[key] = None
