import os

import jinja2

MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180

AUTOPILOT = "Autopilot"
GCS = "GCS"

HEARTBEAT = "HEARTBEAT"
AUTOPILOT_HEARTBEAT_TIMEOUT = 5
GCS_HEARTBEAT_TIMEOUT = 5
HEARTBEAT_TIMEOUT = 2

HEARTBEAT_SEND_RATE_HZ = 1
# MESSAGE_CHECK_INTERVAL = 0.01

SYS_STATUS = "SYS_STATUS"


def valid_latitude_and_longitude(lat, lon):
    if lat < MIN_LATITUDE or lat > MAX_LATITUDE:
        return False
    if lon < MIN_LONGITUDE or lon > MAX_LONGITUDE:
        return False
    return True


def get_logging_config():
    nav_dir = get_nav_dir()

    # Load the logging configuration template file.
    template_loader = jinja2.FileSystemLoader(searchpath=nav_dir)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("logging.conf")

    log_file_abs_path = os.path.join(nav_dir, "app.log")

    # Render the template with variables.
    logging_config = template.render(log_file_path=log_file_abs_path)
    return logging_config


def get_nav_dir():
    curr_path = os.path.dirname(__file__)
    nav_dir = os.path.abspath(os.path.join(curr_path, os.pardir, os.pardir, os.pardir))
    return nav_dir
