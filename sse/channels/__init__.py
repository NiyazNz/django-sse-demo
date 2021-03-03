from abc import ABCMeta


class ChannelsLayer(metaclass=ABCMeta):
    def __init__(self, channel_name: str, *args, **kwargs) -> None:
        """
        Channels layer base class
        """
        self.channel_name = channel_name

    async def receive(self):
        """
        Await and yield a new event message when one is available
        """
        raise NotImplementedError

    async def send(self, message):
        """
        Send message.

        Not actually required to implement for SSE.
        """
        raise NotImplementedError

    async def close(self):
        """
        Close resources
        """
        raise NotImplementedError
