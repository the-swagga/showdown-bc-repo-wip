import asyncio
import csv
import os

from poke_env.player import Player
from poke_env.battle import Field, SideCondition, Weather
from torch.distributions import LogNormal

# BUG: Weather and Terrain is not seen by poke env until the turn after it is set

FIELDNAMES = [
    "weather",
    "weather_turns_left",
    "terrain",
    "terrain_turns_left",
    "trick_room",
    "trick_room_turns_left",
    "my_side_stealth_rock",
    "opp_side_stealth_rock",
    "my_side_spikes",
    "opp_side_spikes",
    "my_side_toxic_spikes",
    "opp_side_toxic_spikes",
    "my_side_sticky_web",
    "opp_side_sticky_web",
    "my_side_light_screen",
    "opp_side_light_screen",
    "my_side_reflect",
    "opp_side_reflect",
    "my_side_aurora_veil",
    "opp_side_aurora_veil",
    "my_pokemon",
    "my_tera_type",
    "my_is_tera",
    "my_type_1",
    "my_type_2",
    "my_hp",
    "my_status",
    "my_boosts",
    "my_team",
    "opp_pokemon",
    "opp_is_tera",
    "opp_type_1",
    "opp_type_2",
    "opp_hp",
    "opp_status",
    "opp_boosts",
    "opp_team",
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
            weather_tl = weather_turns_left(battle)
            terrain_tl = terrain_turns_left(battle)
            if self.prev_state:
                action, weather_setter, terrain_setter = get_action(battle, battle.observations.get(battle.turn - 1))
                print(action)
                if action:
                    if weather_setter:
                        weather_tl = 8
                    if terrain_setter:
                        terrain_tl = 5
                    self.battle_data.append({**self.prev_state, "action": action})

            # --- Debug --- #
            print()

            my = battle.active_pokemon
            opp = battle.opponent_active_pokemon

            self.prev_state = {
                # --- Battle State Data --- #
                "weather": get_weather(battle),
                "weather_turns_left": weather_tl,
                "terrain": get_terrain(battle),
                "terrain_turns_left": terrain_tl,
                "trick_room": get_trick_room(battle),
                "trick_room_turns_left": trick_room_turns_left(battle),
                "my_side_stealth_rock": get_my_side_stealth_rock(battle),
                "opp_side_stealth_rock": get_opp_side_stealth_rock(battle),
                "my_side_spikes": get_my_side_spikes(battle),
                "opp_side_spikes": get_opp_side_spikes(battle),
                "my_side_toxic_spikes": get_my_side_toxic_spikes(battle),
                "opp_side_toxic_spikes": get_opp_side_toxic_spikes(battle),
                "my_side_sticky_web": get_my_side_sticky_web(battle),
                "opp_side_sticky_web": get_opp_side_sticky_web(battle),
                "my_side_light_screen": get_my_side_screen(battle, "LIGHT_SCREEN"),
                "opp_side_light_screen": get_opp_side_screen(battle, "LIGHT_SCREEN"),
                "my_side_reflect": get_my_side_screen(battle, "REFLECT"),
                "opp_side_reflect": get_opp_side_screen(battle, "REFLECT"),
                "my_side_aurora_veil": get_my_side_screen(battle, "AURORA_VEIL"),
                "opp_side_aurora_veil": get_opp_side_screen(battle, "AURORA_VEIL"),

                # --- My Pokemon State Data --- #
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
            final_action, weather_setter, terrain_setter = get_action(battle, battle.observations.get(battle.turn))
            if final_action:
                if weather_setter:
                    self.prev_state["weather_turns_left"] = 8
                if terrain_setter:
                    self.prev_state["terrain_turns_left"] = 5
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
        return None, False, False

    for event in observation.events:
        if len(event) < 4 or battle.player_role not in event[2]:
            continue

        if event[1] in ("move", "switch"):
            species = event[3].split(",")[0].lower().replace(" ", "").replace("-", "")
            return event[3], is_weather_setter(species), is_terrain_setter(species)

    return None, False, False


# --- Special Case Processing --- #

WEATHER_SETTERS = {"kyogre", "pelipper", "politoed", "koraidon", "groudon", "torkoal", "ninetales", "vulpix", "tyranitar", "hippowdown", "gigalith"}
def is_weather_setter(species):
    return species in WEATHER_SETTERS

TERRAIN_SETTERS = {"miraidon", "tapukoko", "pincurchin", "tapubulu", "rillaboom", "thwackey", "tapufini", "weezinggalar", "tapulele", "indeedee", "indeedee-f", "indeedee-m"}
def is_terrain_setter(species):
    return species in TERRAIN_SETTERS

# --- Weather Processing --- #

def get_weather(battle):
    if not battle.weather:
        return None

    for weather in battle.weather:
        return weather.name

def get_weather_duration(battle):
    for weather in battle.weather:
        if weather == Weather.RAINDANCE or weather == Weather.SUNNYDAY:
            return 8
    return 5

weather_seen = {}
def weather_turns_left(battle):
    if not battle.weather:
        return 0

    for weather in list(weather_seen):
        if weather not in battle.weather:
            del weather_seen[weather]
    for weather in battle.weather:
        if weather not in weather_seen:
            weather_seen[weather] = battle.turn

    turns_left = 0
    for weather in battle.weather:
        start_turn = weather_seen[weather]
        weather_duration = get_weather_duration(battle)
        turns_left = weather_duration - (battle.turn - start_turn)
        if turns_left < 0:
            turns_left = 0

        return turns_left


# --- Terrain Processing --- #

def get_terrain(battle):
    if not battle.fields:
        return False

    for field in battle.fields:
        if field.is_terrain:
            return field

    return None

def terrain_turns_left(battle):
    if not battle.fields:
        return 0

    turns_left = 0
    for field, start_turn in battle.fields.items():
        if field.is_terrain:
            turns_left = 5 - (battle.turn - start_turn)
            if turns_left < 0:
                turns_left = 0
            break

    return turns_left


# --- Trick Room Processing --- #

def get_trick_room(battle):
    if not battle.fields:
        return False

    for field in battle.fields:
        if field == Field.TRICK_ROOM:
            return True

    return False

def trick_room_turns_left(battle):
    if not battle.fields:
        return 0

    turns_left = 0
    for field, start_turn in battle.fields.items():
        if field == Field.TRICK_ROOM:
            turns_left = 5 - (battle.turn - start_turn)
            if turns_left < 0:
                turns_left = 0
            break

    return turns_left


# --- Hazards Processing --- #

def get_my_side_stealth_rock(battle):
    return SideCondition.STEALTH_ROCK in battle.side_conditions

def get_opp_side_stealth_rock(battle):
    return SideCondition.STEALTH_ROCK in battle.opponent_side_conditions

def get_my_side_spikes(battle):
    return battle.side_conditions.get(SideCondition.SPIKES, 0)

def get_opp_side_spikes(battle):
    return battle.opponent_side_conditions.get(SideCondition.SPIKES, 0)

def get_my_side_toxic_spikes(battle):
    return battle.side_conditions.get(SideCondition.TOXIC_SPIKES, 0)

def get_opp_side_toxic_spikes(battle):
    return battle.opponent_side_conditions.get(SideCondition.TOXIC_SPIKES, 0)

def get_my_side_sticky_web(battle):
    return SideCondition.STICKY_WEB in battle.side_conditions

def get_opp_side_sticky_web(battle):
    return SideCondition.STICKY_WEB in battle.opponent_side_conditions


# --- Screens Processing --- #

def get_my_side_screen(battle, screen):
    if screen == "LIGHT_SCREEN":
        return SideCondition.LIGHT_SCREEN in battle.side_conditions
    elif screen == "REFLECT":
        return SideCondition.REFLECT in battle.side_conditions
    elif screen == "AURORA_VEIL":
        return SideCondition.AURORA_VEIL in battle.side_conditions

def get_opp_side_screen(battle, screen):
    if screen == "LIGHT_SCREEN":
        return SideCondition.LIGHT_SCREEN in battle.opponent_side_conditions
    elif screen == "REFLECT":
        return SideCondition.REFLECT in battle.opponent_side_conditions
    elif screen == "AURORA_VEIL":
        return SideCondition.AURORA_VEIL in battle.opponent_side_conditions

def get_my_side_screen_turns_left(battle, screen):
    if not get_my_side_screen(battle, screen):
        return 0

    if screen == "LIGHT_SCREEN":
        start_turn = battle.side_conditions[SideCondition.LIGHT_SCREEN]
    elif screen == "REFLECT":
        start_turn = battle.side_conditions[SideCondition.REFLECT]
    elif screen == "AURORA_VEIL":
        start_turn = battle.side_conditions[SideCondition.AURORA_VEIL]
    else:
        return 0

    turns_left = 8 - (battle.turn - start_turn)
    if turns_left < 1:
        turns_left = 1

    return turns_left

def get_opp_side_screen_turns_left(battle, screen):
    if not get_opp_side_screen(battle, screen):
        return 0

    if screen == "LIGHT_SCREEN":
        start_turn = battle.opponent_side_conditions[SideCondition.LIGHT_SCREEN]
    elif screen == "REFLECT":
        start_turn = battle.opponent_side_conditions[SideCondition.REFLECT]
    elif screen == "AURORA_VEIL":
        start_turn = battle.opponent_side_conditions[SideCondition.AURORA_VEIL]
    else:
        return 0

    turns_left = 8 - (battle.turn - start_turn)
    if turns_left < 1:
        turns_left = 1

    return turns_left