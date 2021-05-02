import random

def subscribe_to_channel(channel: str) -> None:
    if random.randint(0,1):
        raise RuntimeError("Error in twitch module, func subscribe_to_channel")