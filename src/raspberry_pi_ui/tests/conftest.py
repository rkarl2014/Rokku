import logging
import logging.config
import os

import pytest
import yaml

from src.pi_to_pi.utility import set_up_pub_sub
from src.raspberry_pi_driver.utility import hash_prefix, terminate_proc
from src.raspberry_pi_ui.rokku import Main


# For more info about pytest.fixture, read
# http://doc.pytest.org/en/latest/fixture.html#fixture-finalization-executing-teardown-code
# and https://pybit.es/pytest-fixtures.html
# Note the use of "package" scope. It is important because we want all
# test files within this testing package to share the same resources.
# A "module" scope only guarantees all testing function within the same
# test file has the same resource, but new resources will be created for
# a different file. We do not want that.
@pytest.fixture(scope="package")
def mqtt_out():
    """Set up mqtt components of rpi_out."""
    mqtt_out = set_up_pub_sub(
        hash_prefix("Rokku/test_topic"), "out_to_in", "in_to_out"
    )
    yield mqtt_out
    print("tear down mqtt_out")
    _, _, out_listen_proc = mqtt_out
    terminate_proc(out_listen_proc)


@pytest.fixture(scope="package")
def button():
    """Set up button via ui."""
    in_pub, in_msg_q, in_listen_proc = set_up_pub_sub(
        hash_prefix("Rokku/test_topic"), "in_to_out", "out_to_in"
    )
    ui = Main(in_pub, in_msg_q)
    yield ui.talk_button
    print("tear down button via UI")
    ui.close_application("", "")
    terminate_proc(in_listen_proc)


@pytest.fixture(scope="package")
def logger():
    """Set up logger for testing."""
    with open(
        f"{os.path.dirname(__file__)}/fixtures/test_logger_config.yaml", "r"
    ) as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    yield logging.getLogger("TEST")
