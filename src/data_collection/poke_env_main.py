import os
from dotenv import load_dotenv
import asyncio
from poke_env.player import Player
from poke_env import AccountConfiguration, ShowdownServerConfiguration

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
BATTLE_FORMAT = os.getenv("BATTLE_FORMAT")

class TurnObserver(Player):
    def choose_move(self, battle):
        # Abstract method
        pass


def init_observer_and_connect():
    turn_observer = TurnObserver(account_configuration=AccountConfiguration(USERNAME, PASSWORD),
                                 server_configuration=ShowdownServerConfiguration,
                                 battle_format=BATTLE_FORMAT)
    return turn_observer

async def queue_for_battle(turn_observer):
    await turn_observer.ladder(1)


async def main():
    print(USERNAME)
    print(PASSWORD)

if __name__ == "__main__":
    asyncio.run(main())
