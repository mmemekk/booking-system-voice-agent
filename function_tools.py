from livekit.agents.llm import function_tool
from typing import Annotated
from pydantic import Field
from datetime import datetime
from agent import logger
from livekit.agents.voice import RunContext

@function_tool()
async def update_name(
    name: Annotated[str, Field(description="The customer's name")],
    context: RunContext
) -> str:
    """Called when the customer provides their name.
    Confirm the spelling with the user before calling the function."""
    userdata = context.userdata
    userdata.customer_name = name
    logger.info("User Data Updated: ")
    logger.info(userdata.summarize())
    return f"The name is updated to {name}"

@function_tool()
async def update_phone(
    phone: Annotated[str, Field(description="The customer's phone number")],
    context: RunContext,
) -> str:
    """Called when the customer provides their phone number.
    """
    userdata = context.userdata
    userdata.customer_phone = phone
    logger.info("User Data Updated: ")
    logger.info(userdata.summarize())
    return f"The phone number is updated to {phone}"

@function_tool()
#must use try catch block if Value Error
async def update_reservation_date(
    reservation_date: Annotated[str, Field(description="The customer's reservation date. Must be in YYYY-MM-DD format")],
    context: RunContext,
) -> str:
    """Called when the customer provides their reservation date.
    """
    userdata = context.userdata
    userdata.reservation_date = datetime.strptime(reservation_date, '%Y-%m-%d').date()
    logger.info("User Data Updated: ")
    logger.info(userdata.summarize())
    return f"The reservation date is updated to {reservation_date}"

@function_tool()
#must use try catch block if Value Error
async def update_reservation_time(
    reservation_time: Annotated[str, Field(description="The customer's reservation time. Must be in HH:MM format")],
    context: RunContext,
) -> str:
    """Called when the customer provides their reservation time.
    """
    userdata = context.userdata
    logger.info(f"Received reservation_time: {reservation_time}")
    userdata.reservation_time = datetime.strptime(reservation_time, '%H:%M').time()
    logger.info("User Data Updated: ")
    logger.info(userdata.summarize())
    return f"The reservation date is updated to {reservation_time}"

__all__ = [
    "update_name",
    "update_phone",
    "update_reservation_date",
    "update_reservation_time",
]