import logging
import yaml

from dataclasses import dataclass
from typing import Annotated, Optional
from pydantic import Field
from datetime import date, time

from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import AgentServer, room_io
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent, AgentSession, RunContext
from livekit.plugins import (google,noise_cancellation)

logger = logging.getLogger("AGENT-MANAGEMENT")
logger.setLevel(logging.INFO)

load_dotenv()

@dataclass
class UserData:

    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    reservation_date: Optional[date] = None
    reservation_time: Optional[time] = None
    # reservation_date: Optional[date] = date(2025,9,2)
    # reservation_time: Optional[time] = time(19,7)
    reservation_capacity: Optional[int] = None
    special_request: Optional[str] = None

    def summarize(self) -> str:
        # DATE_FORMAT = "%Y-%m-%d"
        # TIME_FORMAT = "%H:%M"   
        data = {
            "customer_name": self.customer_name or "unknown",
            "customer_phone": self.customer_phone or "unknown",
            "reservation_date": self.reservation_date or "unknown",
            "reservation_time": self.reservation_time or "unknown",
            # "reservation_date": self.reservation_date.strftime(DATE_FORMAT) or "unknown",
            # "reservation_time": self.reservation_time.strftime(TIME_FORMAT) or "unknown",
            "reservation_capacity": self.reservation_capacity or "unknown",
            "special_request": self.special_request or "none",
        }

        return yaml.dump(data)

RunContext_T = RunContext[UserData]


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")

    @function_tool()
    async def update_name(
        self,
        name: Annotated[str, Field(description="The customer's name")],
        context: RunContext_T,
    ) -> str:
        """Called when the user provides their name.
        Confirm the spelling with the user before calling the function."""
        userdata = context.userdata
        userdata.customer_name = name
        logger.info(userdata.summarize())
        return f"The name is updated to {name}"

server = AgentServer()

@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    userdata = UserData()

    session = AgentSession[UserData](
        userdata=userdata,
        llm=google.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            voice="Puck",
            temperature=0.8,
        ),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(),
            ),
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance. You should start by speaking in English."
    )


if __name__ == "__main__":
    agents.cli.run_app(server)