import logging
from dataclasses import dataclass, field
from typing import Annotated, Optional
from datetime import date, time
import yaml


from livekit.agents import AgentServer, JobContext, cli
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent, AgentSession, RunContext
from livekit.plugins import google



@dataclass
class UserData:

    customer_name: Optional[str] = "mekk"
    customer_phone: Optional[str] = None
    reservation_date: Optional[date] = date(2025,9,2)
    reservation_time: Optional[time] = time(19,7)
    reservation_capacity: Optional[int] = None
    special_request: Optional[str] = None

    agents: dict[str, Agent] = field(default_factory=dict)
    prev_agent: Optional[Agent] = None

    def summarize(self) -> str:
        DATE_FORMAT = "%Y-%m-%d"
        TIME_FORMAT = "%H:%M"   
        data = {
            "customer_name": self.customer_name or "unknown",
            "customer_phone": self.customer_phone or "unknown",
            "reservation_date": self.reservation_date.strftime(DATE_FORMAT) or "unknown",
            "reservation_time": self.reservation_time.strftime(TIME_FORMAT) or "unknown",
            "reservation_capacity": self.reservation_capacity or "unknown",
            "special_request": self.special_request or "none",
        }
        # summarize in yaml performs better than json
        return yaml.dump(data)

x=UserData()
print(x.summarize())