from django.http import ServerSentEventsResponse
from sse.channels import ChannelsLayer


class ChannelsSseResponse(ServerSentEventsResponse):
    def __init__(self, channels_layer: ChannelsLayer, *args, **kwargs):
        self.channels_layer = channels_layer
        super().__init__(self.channels_layer.receive, *args, **kwargs)
        self.add_resource_closer(self.channels_layer.close)
