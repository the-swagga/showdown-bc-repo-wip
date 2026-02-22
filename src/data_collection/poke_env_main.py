import os
from dotenv import load_dotenv
import asyncio
from poke_env import AccountConfiguration, ShowdownServerConfiguration
from poke_env_turn_observer import TurnObserver

load_dotenv()
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
FORMAT = os.getenv("FORMAT")


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
        print()
        await queue_for_battle(bot)
        print()
        print("Battle finished.")
        print()


if __name__ == "__main__":
    asyncio.run(main())
