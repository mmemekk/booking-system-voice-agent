import logging

from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentServer, room_io, TurnHandlingOptions, inference, WorkerOptions, JobProcess
from livekit.agents.voice import Agent, AgentSession, RunContext
from livekit.plugins import google,noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
import asyncio

from instruction_loader import load_agent_instruction, load_greet_instruction
from function_tools import *
from userdata import UserData
from transfer_utils import transfer_call

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

def prewarm(proc: JobProcess):
    # Load heavy models here so they stay in memory
    proc.userdata["vad"] = silero.VAD.load()
    
server = AgentServer()
server.setup_fnc = prewarm


@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    INSTRUCTION = load_agent_instruction()
    GREET_INSTURCTION = load_greet_instruction()
    userdata = UserData()
    
    session = AgentSession[UserData](
        userdata=userdata,
        stt=inference.STT(
            model="deepgram/nova-3",
            language="en",
            extra_kwargs={"numerals": True},
        ),
        
        llm="openai/gpt-4.1-mini",
        tts=inference.TTS(
            model="cartesia/sonic-3", 
            voice="47c38ca4-5f35-497b-b1a3-415245fb35e1", 
            language="en",
            extra_kwargs={
                "speed": 0.9,
                "volume": 1.0,
                "emotion": "excited"
            }
        ),
        turn_handling=TurnHandlingOptions(
            turn_detection=MultilingualModel(),
        ),
        # vad=silero.VAD.load(),
        vad = ctx.proc.userdata["vad"],

    )
    
    @ctx.room.on("sip_dtmf_received")
    def handle_dtmf(dtmf: rtc.SipDTMF):
        if dtmf.digit == "0":
            logger.info("🚨 User pressed 0! Transfering to Restaurant.")
            session.interrupt()
            async def execute_transfer_sequence():
                await session.say(
                    "Transferring you to an operator now, please hold on.",
                    allow_interruptions=False
                )
                await transfer_call(
                    participant_identity=dtmf.participant.identity,
                    room_name=ctx.room.name,
                )
            asyncio.create_task(execute_transfer_sequence())
    
    await session.start(
        room=ctx.room,
        agent=Assistant(INSTRUCTION),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(),
            ),
        ),
    )
    
    participant = await ctx.wait_for_participant()
    if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:

        phone_number = participant.attributes.get('sip.phoneNumber', 'unknown')
        logger.info(f"SIP caller joined from phone number: {phone_number}")
        formattedPhoneNumber = "0"+phone_number[3:]
        userdata.customer_phone = formattedPhoneNumber
        
        logger.info(userdata.summarize())
    else:
        logger.info(f"Non-SIP participant joined: {participant.identity}")
    
    await session.say(
        "Good Morning",
        allow_interruptions=False
    )


if __name__ == "__main__":
    agents.cli.run_app(server)