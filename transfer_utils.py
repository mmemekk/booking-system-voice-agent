import asyncio
import logging
import os

from livekit import api
from livekit.protocol.sip import TransferSIPParticipantRequest

logger = logging.getLogger("TRANSFER-UTILS")
logger.setLevel(logging.INFO)

async def transfer_call(participant_identity: str, room_name: str) -> None:
  async with api.LiveKitAPI() as livekit_api:
    transfer_to = 'tel:+66646199242'

    try:
      # Create transfer request
      transfer_request = TransferSIPParticipantRequest(
          participant_identity=participant_identity,
          room_name=room_name,
          transfer_to=transfer_to,
          play_dialtone=True
      )
      
      logger.debug(f"Transfer request: {transfer_request}")
          
      # Transfer caller
      await livekit_api.sip.transfer_sip_participant(transfer_request)
      print("SIP participant transferred successfully")
          
    except Exception as error:
        # Check if it's a Twirp error with metadata
        if hasattr(error, 'metadata') and error.metadata:
            print(f"SIP error code: {error.metadata.get('sip_status_code')}")
            print(f"SIP error message: {error.metadata.get('sip_status')}")
        else:
            print(f"Error transferring SIP participant:")
            print(f"{error.status} - {error.code} - {error.message}")