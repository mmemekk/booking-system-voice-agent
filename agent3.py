import logging
from dataclasses import dataclass, field
from typing import Annotated, Optional

import yaml
from dotenv import load_dotenv
from pydantic import Field

from livekit.agents import AgentServer, JobContext, cli
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent, AgentSession, RunContext
from livekit.plugins import google

# from livekit.plugins import noise_cancellation

# This example demonstrates a multi-agent system where tasks are delegated to sub-agents
# based on the user's request.
#
# The user is initially connected to a greeter, and depending on their need, the call is
# handed off to other agents that could help with the more specific tasks.
# This helps to keep each agent focused on the task at hand, and also reduces costs
# since only a subset of the tools are used at any given time.


logger = logging.getLogger("restaurant-example")
logger.setLevel(logging.INFO)

load_dotenv()


@dataclass
class UserData:

    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    reservation_date: Optional[str] = None
    reservation_time: Optional[str] = None
    reservation_capacity: Optional[int] = None
    special_request: Optional[str] = None

    agents: dict[str, Agent] = field(default_factory=dict)
    prev_agent: Optional[Agent] = None

    def summarize(self) -> str:
        data = {
            "customer_name": self.customer_name or "unknown",
            "customer_phone": self.customer_phone or "unknown",
            "reservation_date": self.reservation_date or "unknown",
            "reservation_time": self.reservation_time or "unknown",
            "reservation_capacity": self.reservation_capacity or "unknown",
            "special_request": self.special_request or "none",
        }
        # summarize in yaml performs better than json
        return yaml.dump(data)

RunContext_T = RunContext[UserData]


# common functions


@function_tool()
async def update_name(
    name: Annotated[str, Field(description="The customer's name")],
    context: RunContext_T,
) -> str:
    """Called when the user provides their name.
    Confirm the spelling with the user before calling the function."""
    userdata = context.userdata
    userdata.customer_name = name
    return f"The name is updated to {name}"


@function_tool()
async def update_phone(
    phone: Annotated[str, Field(description="The customer's phone number")],
    context: RunContext_T,
) -> str:
    """Called when the user provides their phone number.
    Confirm the spelling with the user before calling the function."""
    userdata = context.userdata
    userdata.customer_phone = phone
    return f"The phone number is updated to {phone}"


@function_tool()
async def to_greeter(context: RunContext_T) -> Agent:
    """Called when user asks any unrelated questions or requests
    any other services not in your job description."""
    curr_agent: BaseAgent = context.session.current_agent
    return await curr_agent._transfer_to_agent("greeter", context)


class BaseAgent(Agent):
    async def on_enter(self) -> None:
        agent_name = self.__class__.__name__
        logger.info(f"entering task {agent_name}")

        userdata: UserData = self.session.userdata
        chat_ctx = self.chat_ctx.copy()

        # add the previous agent's chat history to the current agent
        if isinstance(userdata.prev_agent, Agent):
            # print("RAW",userdata.prev_agent.chat_ctx )
            truncated_chat_ctx = userdata.prev_agent.chat_ctx.copy(
                exclude_instructions=True, exclude_function_call=False
            ).truncate(max_items=6)
            existing_ids = {item.id for item in chat_ctx.items}
            items_copy = [item for item in truncated_chat_ctx.items if item.id not in existing_ids]
            # print("ITEM",items_copy)
            chat_ctx.items.extend(items_copy)

        # add an instructions including the user data as assistant message
        chat_ctx.add_message(
            role="system",  # role=system works for OpenAI's LLM and Realtime API
            content=f"You are {agent_name} agent. Current user data is {userdata.summarize()}",
        )
        await self.update_chat_ctx(chat_ctx)
        self.session.generate_reply(instructions="Ask what time do you want to book")

    async def _transfer_to_agent(self, name: str, context: RunContext_T) -> tuple[Agent, str]:
        userdata = context.userdata
        current_agent = context.session.current_agent
        next_agent = userdata.agents[name]
        userdata.prev_agent = current_agent

        return next_agent, f"Transferring to {name}."


class Greeter(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                f"You are a friendly restaurant receptionist.\n"
                "Your jobs are to greet the caller and understand if they want to "
                "make a reservation or order takeaway. Guide them to the right agent using tools."
            ),
        )

    @function_tool()
    async def to_reservation(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when user wants to make or update a reservation.
        This function handles transitioning to the reservation agent
        who will collect the necessary details like reservation time,
        customer name and phone number."""
        return await self._transfer_to_agent("reservation", context)

    @function_tool()
    async def to_generalInfo(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when the user wants to ask general questions about the restaurant like parking, business hour."""
        return await self._transfer_to_agent("generalInfo", context)


class Reservation(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are a reservation agent at a restaurant. Your jobs are to ask for "
            "the reservation time, then customer's name, and phone number. Then "
            "confirm the reservation details with the customer.",
            tools=[update_name, update_phone, to_greeter],
        )


class GeneralInfo(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            instructions="greet the user and tell them that you are a general information agent. "
        )


server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext):
    userdata = UserData()
    userdata.agents.update(
        {
            "greeter": Greeter(),
            "reservation": Reservation(),
            "generalInfo": GeneralInfo(),
        }
    )
    session = AgentSession[UserData](
        userdata=userdata,
        llm=google.realtime.RealtimeModel(
        model="gemini-2.5-flash-native-audio-preview-09-2025",
        voice="Puck",
        temperature=0.8,
        ),
    )

    await session.start(
        agent=userdata.agents["greeter"],
        room=ctx.room,
    )

    # await agent.say("Welcome to our restaurant! How may I assist you today?")


if __name__ == "__main__":
    cli.run_app(server)