from .UnboundCommandBase import *


class Dscan(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.resp = "The Dscan service is currently in development!"

    async def get_text(self, d_message: discord.Message, message_text: str, **kwargs)->str:
        return self.resp



