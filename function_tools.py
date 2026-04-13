from livekit.agents.llm import function_tool
from typing import Annotated
from pydantic import Field
from datetime import datetime
from agent import logger
from livekit.agents.voice import RunContext
from livekit.agents import (utils, ToolError)
import aiohttp
import asyncio

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

@function_tool()
async def update_party_size(
    party_size: Annotated[int, Field(description="The customer's party size")],
    context: RunContext,
) -> str:
    """Called when the customer provides their party size.
    """
    userdata = context.userdata
    userdata.party_size = party_size
    logger.info("User Data Updated: ")
    logger.info(userdata.summarize())
    return f"The party size is updated to {party_size}"

@function_tool()
async def update_special_request(
    special_request: Annotated[str, Field(description="The customer's special request")],
    context: RunContext,
) -> str:
    """Called when the customer provides their special request regarding their booking.
    """
    userdata = context.userdata
    userdata.special_request = special_request
    logger.info("User Data Updated: ")
    logger.info(userdata.summarize())
    return f"The special request is updated to {special_request}"

@function_tool()
async def check_availability(
    context: RunContext,
) -> str:
    """Called to check table availability.
    """
    url = "https://booking-system-backend-production-54ed.up.railway.app/booking/3/check"
    
    await context.session.say(" Just a moment please ")
    await asyncio.sleep(0.5)
    requestBody = context.userdata.check_availability_request()
    print(requestBody)
    try:
        http_session = utils.http_context.http_session()
        timeout = aiohttp.ClientTimeout(total=10) 
        async with http_session.post(url, json=requestBody, timeout=timeout) as resp:
            if resp.status >= 400:
                raise ToolError(f"error: HTTP {resp.status}")
            return await resp.text()
    except ToolError:
        raise
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            raise ToolError(f"error: {e!s}") from e

@function_tool()
async def create_reservation(
    context: RunContext,
) -> str:
    """Call this to create the booking reservation.
    """
    url = "https://booking-system-backend-production-54ed.up.railway.app/booking/3"
    
    await context.session.say(" Great! Just a moment please. I'm createing your reservation. ")
    await asyncio.sleep(0.5)
    requestBody = context.userdata.create_reservation_request()
    print(requestBody)
    try:
        http_session = utils.http_context.http_session()
        timeout = aiohttp.ClientTimeout(total=5)
        async with http_session.post(url, json=requestBody, timeout=timeout) as resp:
            if resp.status >= 400:
                raise ToolError(f"error: HTTP {resp.status}")
            return await resp.text()
    except ToolError:
        raise
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            raise ToolError(f"error: {e!s}") from e
        

__all__ = [
    "update_name",
    "update_phone",
    "update_reservation_date",
    "update_reservation_time",
    "update_party_size",
    "update_special_request",
    "check_availability",
    "create_reservation",
]