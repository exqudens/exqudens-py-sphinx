import logging


def pytest_sessionstart(session):
    logging.info("before-all")


def pytest_sessionfinish(session, exitstatus):
    print("\n")
    logging.info("after-all")
