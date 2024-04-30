"""This script runs on the drone and serves as the process waiting to activate
flight termination."""

import asyncio
import io
import logging
import logging.config
import os
import sys

from dotenv import load_dotenv

from flight_termination.flight_termination import begin_flight_termination
from navigation.connection import (
    AutopilotConnectionWrapper,
    heartbeat_loop,
    receive_msg_loop,
    validate_connection_loop,
)
from navigation.utils import get_logging_config

# Reload environment variables on startup to avoid caching them.
load_dotenv(verbose=True, override=True)

# Configure logging.
logging_config = get_logging_config()
logging.config.fileConfig(io.StringIO(logging_config), disable_existing_loggers=False)

logger = logging.getLogger()


async def main():
    try:
        autopilot_conn_string = os.getenv("AUTOPILOT_CONN_STRING")
        autopilot_baudrate = os.getenv("AUTOPILOT_BAUDRATE")

        autopilot_conn_wrapper = AutopilotConnectionWrapper(
            autopilot_conn_string, autopilot_baudrate
        )
        if not autopilot_conn_wrapper.conn:
            sys.exit(1)

        # Wait for a heartbeat from the autopilot before sending commands.
        autopilot_conn_wrapper.conn.wait_heartbeat()
        autopilot_conn_wrapper.update_last_heartbeat()
        logger.info("Initial heartbeat received from the autopilot.")

        # Request messages from the flight controller.
        autopilot_conn_wrapper.request_messages()

        # Gather asynchronous tasks.
        receive_task = asyncio.create_task(receive_msg_loop(autopilot_conn_wrapper))
        heartbeat_task = asyncio.create_task(heartbeat_loop(autopilot_conn_wrapper))
        validate_connection_task = asyncio.create_task(
            validate_connection_loop(autopilot_conn_wrapper)
        )

        try:
            await asyncio.gather(receive_task, heartbeat_task, validate_connection_task)
        except Exception as error:
            logger.info(error)
            logger.info("Beginning flight termination...")
            begin_flight_termination()

    except KeyboardInterrupt:
        logger.info("Exiting...")
        autopilot_conn_wrapper.conn.close()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
