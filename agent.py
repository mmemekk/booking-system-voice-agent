import logging

from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import AgentServer, room_io
from livekit.agents.voice import Agent, AgentSession, RunContext
from livekit.plugins import (google,noise_cancellation)

from instruction import INSTRUCTION
from function_tools import *
from userdata import UserData

logger = logging.getLogger("AGENT-MANAGEMENT")
logger.setLevel(logging.INFO)

load_dotenv()

RunContext_T = RunContext[UserData]

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=INSTRUCTION,
            tools=[
                update_name,
                update_phone,
                update_reservation_date,
                update_reservation_time
            ]
        )

server = AgentServer()

@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    userdata = UserData()

    session = AgentSession[UserData](
        userdata=userdata,
        llm=google.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            voice="Puck",
            temperature=0.5,
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