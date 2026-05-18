import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="run @pytest.mark.live tests against the real chenki-llm HF Space",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--live"):
        return
    skip_live = pytest.mark.skip(reason="live test (pass --live to run)")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)
