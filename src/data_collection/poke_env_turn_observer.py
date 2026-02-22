import asyncio
import csv
import os
from poke_env.player import Player


FIELDNAMES = [
    "weather", "my_side_hazards", "opp_side_hazards", "terrain",
    "my_pokemon", "my_tera_type", "my_is_tera", "my_type_1", "my_type_2",
    "my_hp", "my_status", "my_boosts", "my_team",
    "opp_pokemon", "opp_is_tera", "opp_type_1", "opp_type_2",
    "opp_hp", "opp_status", "opp_boosts", "opp_team",
    "action"
]


class TurnObserver(Player):
    # Extends Poke-env Player Class

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prev_state = None
        self.battle_data = []
        self.csv_path = "test.csv"

    async def choose_move(self, battle):
        # Overrides Poke-env choose_move method

        if not battle.force_switch:
            if self.prev_state:
                action = get_action(battle, battle.observations.get(battle.turn - 1))
                print(action)
                if action:
                    self.battle_data.append({**self.prev_state, "action": action})

            my_active_mon = battle.active_pokemon
            opp_active_mon = battle.opponent_active_pokemon
            my_team = battle.team
            opp_team = battle.opponent_team

            print(battle.current_observation)
            print()

            # --- Battle State --- #
            print(f"Weather: {battle.weather}")
            print(f"My side hazards: {battle.side_conditions}")
            print(f"Opponent side hazards: {battle.opponent_side_conditions}")
            print(f"Terrain: {battle.fields}")
            print()

            # --- Player State --- #
            print(f"My team: {my_team}")
            print(f"My pokemon: {my_active_mon.species}")
            print(f"Tera type: {my_active_mon.tera_type}")
            print(f"Is tera: {my_active_mon.is_terastallized}")
            print(f"Primary type: {my_active_mon.type_1}")
            print(f"Secondary type: {my_active_mon.type_2}")
            print(f"HP: {my_active_mon.current_hp_fraction}")
            print(f"Status: {my_active_mon.status}")
            print(f"Boosts: {my_active_mon.boosts}")
            print()

            # --- Opponent State --- #
            print(f"Opponent team: {opp_team}")
            print(f"Opponent pokemon: {opp_active_mon.species}")
            print(f"Is tera: {opp_active_mon.is_terastallized}")
            print(f"Primary type: {opp_active_mon.type_1}")
            print(f"Secondary type: {opp_active_mon.type_2}")
            print(f"HP: {opp_active_mon.current_hp_fraction}")
            print(f"Status: {opp_active_mon.status}")
            print(f"Boosts: {opp_active_mon.boosts}")
            print()

            my = battle.active_pokemon
            opp = battle.opponent_active_pokemon

            self.prev_state = {
                "weather": str(battle.weather),
                "my_side_hazards": str(battle.side_conditions),
                "opp_side_hazards": str(battle.opponent_side_conditions),
                "terrain": str(battle.fields),
                "my_pokemon": my.species,
                "my_tera_type": my.tera_type,
                "my_is_tera": my.is_terastallized,
                "my_type_1": my.type_1,
                "my_type_2": my.type_2,
                "my_hp": my.current_hp_fraction,
                "my_status": my.status,
                "my_boosts": str(my.boosts),
                "my_team": str({p.species: p.current_hp_fraction for p in battle.team.values()}),
                "opp_pokemon": opp.species if opp else None,
                "opp_is_tera": opp.is_terastallized if opp else None,
                "opp_type_1": opp.type_1 if opp else None,
                "opp_type_2": opp.type_2 if opp else None,
                "opp_hp": opp.current_hp_fraction if opp else None,
                "opp_status": opp.status if opp else None,
                "opp_boosts": str(opp.boosts) if opp else None,
                "opp_team": str({p.species: p.current_hp_fraction for p in battle.opponent_team.values()}),
            }

        try:
            await asyncio.sleep(float("inf"))
        except asyncio.CancelledError:
            raise

        return self.choose_default_move()

    def _battle_finished_callback(self, battle):
        if self.prev_state:
            final_action = get_action(battle, battle.observations.get(battle.turn))
            if final_action:
                self.battle_data.append({**self.prev_state, "action": final_action})

        if self.battle_data:
            if not os.path.exists(self.csv_path):
                with open(self.csv_path, "w", newline="") as f:
                    csv.DictWriter(f, fieldnames=FIELDNAMES).writeheader()
            with open(self.csv_path, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writerows(self.battle_data)
            self.battle_data = []
        super()._battle_finished_callback(battle)


def get_action(battle, observation):
    if observation is None:
        return None

    for event in observation.events:
        if len(event) < 4 or battle.player_role not in event[2]:
            continue

        if event[1] in ("move", "switch"):
            return event[3]

    return None