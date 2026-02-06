import os
from dotenv import load_dotenv
import asyncio
from poke_env.player import Player
from poke_env import AccountConfiguration, ShowdownServerConfiguration

load_dotenv()
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
FORMAT = os.getenv("FORMAT")

class TurnObserver(Player):
    def choose_move(self, battle):
        # Abstract method
        pass


def init_observer_and_connect():
    turn_observer = TurnObserver(account_configuration=AccountConfiguration(USER, PASSWORD),
                                 server_configuration=ShowdownServerConfiguration,
                                 battle_format=FORMAT)
    return turn_observer

async def queue_for_battle(turn_observer):
    await turn_observer.ladder(1)


async def main():
    bot = init_observer_and_connect()

    while True:
        input(f"Press Enter to queue for {FORMAT}...")
        print()
        print(f"Queueing for {FORMAT}")
        await queue_for_battle(bot)
        print("Battle finished.")
        print()


if __name__ == "__main__":
    asyncio.run(main())
