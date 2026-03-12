import logging

from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentServer, room_io
from livekit.agents.voice import Agent, AgentSession, RunContext
from livekit.plugins import (google,noise_cancellation, openai)

from instruction_loader import load_agent_instruction, load_greet_instruction
from function_tools import *
from userdata import UserData

logger = logging.getLogger("AGENT-MANAGEMENT")
logger.setLevel(logging.INFO)

load_dotenv()

RunContext_T = RunContext[UserData]

class Assistant(Agent):
    def __init__(self, instructions: str) -> None:
        super().__init__(
            instructions=instructions,
            tools=[
                update_name,
                update_phone,
                update_reservation_date,
                update_reservation_time,
                update_party_size,
                update_special_request,
                check_availability,
                create_reservation
                
            ]
        )

server = AgentServer()

@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    
    INSTRUCTION = load_agent_instruction()
    GREET_INSTURCTION = load_greet_instruction()
    userdata = UserData()

    session = AgentSession[UserData](
        userdata=userdata,
        llm=google.realtime.RealtimeModel(
            model="gemini-2.5-flash-native-audio-preview-12-2025",
            voice="Puck",
            temperature=0.5,
        ),
        # llm=openai.realtime.RealtimeModel(voice="marin"),
    
    )
    await session.start(
        room=ctx.room,
        agent=Assistant(INSTRUCTION),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(),
            ),
        ),
    )
    await session.generate_reply(
        instructions=GREET_INSTURCTION
    )


if __name__ == "__main__":
    agents.cli.run_app(server)