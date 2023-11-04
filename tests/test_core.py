import logging


class TestCore:
    logger = None

    @classmethod
    def setup_class(cls):
        cls.logger = logging.getLogger('.'.join([__class__.__module__, __class__.__name__]))

    def test_1(self):
        self.logger.info("test-1")
