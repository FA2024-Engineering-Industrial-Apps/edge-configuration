import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-expensive",
        action="store_true",
        default=False,
        help="Run expensive tests",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "expensive: mark test as computationally expensive"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-expensive"):
        # If the --run-expensive flag is set, don't skip any tests
        return
    skip_expensive = pytest.mark.skip(reason="Need --run-expensive option to run")
    for item in items:
        if "expensive" in item.keywords:
            item.add_marker(skip_expensive)
