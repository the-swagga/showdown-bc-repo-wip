import asyncio
import csv
import os

from poke_env.player import Player
from poke_env.battle import Field, SideCondition, Weather, Effect


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
    "my_ability",
    "my_item",
    "my_type_1",
    "my_type_2",
    "my_is_tera",
    "my_can_tera",
    "my_atk_boost",
    "my_def_boost",
    "my_spa_boost",
    "my_spd_boost",
    "my_spe_boost",
    "my_hp",
    "my_status",
    "my_turns_asleep_or_toxic",
    "my_turns_protect",
    "my_effect_1",
    "my_effect_2",
    "my_move_1",
    "my_move_1_category",
    "my_move_1_type",
    "my_move_1_power",
    "my_move_1_accuracy",
    "my_move_1_self_boost",
    "my_move_1_pivot",
    "my_move_1_priority",
    "my_move_2",
    "my_move_2_category",
    "my_move_2_type",
    "my_move_2_power",
    "my_move_2_accuracy",
    "my_move_2_self_boost",
    "my_move_2_pivot",
    "my_move_2_priority",
    "my_move_3",
    "my_move_3_category",
    "my_move_3_type",
    "my_move_3_power",
    "my_move_3_accuracy",
    "my_move_3_self_boost",
    "my_move_3_pivot",
    "my_move_3_priority",
    "my_move_4",
    "my_move_4_category",
    "my_move_4_type",
    "my_move_4_power",
    "my_move_4_accuracy",
    "my_move_4_self_boost",
    "my_move_4_pivot",
    "my_move_4_priority",

    "opp_pokemon",
    "opp_ability",
    "opp_item",
    "opp_type_1",
    "opp_type_2",
    "opp_is_tera",
    "opp_can_tera",
    "opp_atk_boost",
    "opp_def_boost",
    "opp_spa_boost",
    "opp_spd_boost",
    "opp_spe_boost",
    "opp_hp",
    "opp_status",
    "opp_turns_asleep_or_toxic",
    "opp_turns_protect",
    "opp_effect_1",
    "opp_effect_2",
    "opp_move_1",
    "opp_move_2",
    "opp_move_3",
    "opp_move_4",

    "my_switch_1",
    "my_switch_2",
    "my_switch_3",
    "my_switch_4",
    "my_switch_5",
    "opp_switch_1",
    "opp_switch_2",
    "opp_switch_3",
    "opp_switch_4",
    "opp_switch_5",

    "action"
]

class TurnObserver(Player):
    # Extends Poke-env Player Class

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prev_state = None
        self.battle_data = []
        self.csv_path = "test.csv"
        self.opponent_teampreview = None

    def set_opponent_teampreview(self, otp):
        self.opponent_teampreview = otp

    async def choose_move(self, battle):
        # Overrides Poke-env choose_move method

        if battle.teampreview_opponent_team and self.opponent_teampreview is None:
            self.set_opponent_teampreview(battle.teampreview_opponent_team)

        if not battle.force_switch:
            weather_tl = weather_turns_left(battle)
            terrain_tl = terrain_turns_left(battle)
            if self.prev_state:
                action, weather_setter, terrain_setter = get_action(battle, battle.observations.get(battle.turn - 1))
                if action:
                    if weather_setter:
                        weather_tl = 8
                    if terrain_setter:
                        terrain_tl = 5
                    self.battle_data.append({**self.prev_state, "action": action})

            my = battle.active_pokemon
            my_effect_1, my_effect_2 = get_effects(my)
            my_move_1 = get_move_at_index(my, 1)
            my_move_2 = get_move_at_index(my, 2)
            my_move_3 = get_move_at_index(my, 3)
            my_move_4 = get_move_at_index(my, 4)

            opp = battle.opponent_active_pokemon
            opp_effect_1, opp_effect_2 = get_effects(opp)
            opp_move_1 = get_move_at_index(opp, 1)
            opp_move_2 = get_move_at_index(opp, 2)
            opp_move_3 = get_move_at_index(opp, 3)
            opp_move_4 = get_move_at_index(opp, 4)

            my_switches = []
            for i in range(1, 6):
                my_switches.append(safe_my_available_switches(battle, i))
            opp_switches = []
            for i in range(1, 6):
                opp_switches.append(opp_available_switches(battle, self.opponent_teampreview, i))

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

                # --- My Active Pokemon State Data --- #
                "my_pokemon": my.species,
                "my_ability": my.ability,
                "my_item": my.item,
                "my_type_1": my.type_1,
                "my_type_2": my.type_2,
                "my_is_tera": my.is_terastallized,
                "my_can_tera": battle.can_tera,
                "my_atk_boost": get_atk_boost(my),
                "my_def_boost": get_def_boost(my),
                "my_spa_boost": get_spa_boost(my),
                "my_spd_boost": get_spd_boost(my),
                "my_spe_boost": get_spe_boost(my),
                "my_hp": my.current_hp_fraction,
                "my_status": my.status,
                "my_turns_asleep_or_toxic": my.status_counter,
                "my_turns_protect": my.protect_counter,
                "my_effect_1": my_effect_1,
                "my_effect_2": my_effect_2,
                "my_move_1": my_move_1.id if my_move_1 else None,
                "my_move_1_category": my_move_1.category.name if my_move_1 else None,
                "my_move_1_type": my_move_1.type if my_move_1 else None,
                "my_move_1_power": get_max_power(my_move_1),
                "my_move_1_accuracy": my_move_1.accuracy if my_move_1 else None,
                "my_move_1_self_boost": check_self_boost(my_move_1),
                "my_move_1_pivot": my_move_1.self_switch if my_move_1 else None,
                "my_move_1_priority": my_move_1.priority if my_move_1 else None,
                "my_move_2": my_move_2.id,
                "my_move_2_category": my_move_2.category.name if my_move_2 else None,
                "my_move_2_type": my_move_2.type if my_move_2 else None,
                "my_move_2_power": get_max_power(my_move_2),
                "my_move_2_accuracy": my_move_2.accuracy if my_move_2 else None,
                "my_move_2_self_boost": check_self_boost(my_move_2),
                "my_move_2_pivot": my_move_2.self_switch if my_move_2 else None,
                "my_move_2_priority": my_move_2.priority if my_move_2 else None,
                "my_move_3": my_move_3.id,
                "my_move_3_category": my_move_3.category.name if my_move_3 else None,
                "my_move_3_type": my_move_3.type if my_move_3 else None,
                "my_move_3_power": get_max_power(my_move_3),
                "my_move_3_accuracy": my_move_3.accuracy if my_move_3 else None,
                "my_move_3_self_boost": check_self_boost(my_move_3),
                "my_move_3_pivot": my_move_3.self_switch if my_move_3 else None,
                "my_move_3_priority": my_move_3.priority if my_move_3 else None,
                "my_move_4": my_move_4.id,
                "my_move_4_category": my_move_4.category.name if my_move_4 else None,
                "my_move_4_type": my_move_4.type if my_move_4 else None,
                "my_move_4_power": get_max_power(my_move_4),
                "my_move_4_accuracy": my_move_4.accuracy if my_move_4 else None,
                "my_move_4_self_boost": check_self_boost(my_move_4),
                "my_move_4_pivot": my_move_4.self_switch if my_move_4 else None,
                "my_move_4_priority": my_move_4.priority if my_move_4 else None,

                # --- Opponent Active Pokemon State Data --- #
                "opp_pokemon": opp.species,
                "opp_ability": opp.ability,
                "opp_item": opp.item,
                "opp_type_1": opp.type_1,
                "opp_type_2": opp.type_2,
                "opp_is_tera": opp.is_terastallized,
                "opp_can_tera": not battle.opponent_used_tera,
                "opp_atk_boost": get_atk_boost(opp),
                "opp_def_boost": get_def_boost(opp),
                "opp_spa_boost": get_spa_boost(opp),
                "opp_spd_boost": get_spd_boost(opp),
                "opp_spe_boost": get_spe_boost(opp),
                "opp_hp": opp.current_hp_fraction,
                "opp_status": opp.status,
                "opp_turns_asleep_or_toxic": opp.status_counter,
                "opp_turns_protect": opp.protect_counter,
                "opp_effect_1": opp_effect_1,
                "opp_effect_2": opp_effect_2,
                "opp_move_1": opp_move_1.id if opp_move_1 else None,
                "opp_move_2": opp_move_2.id if opp_move_2 else None,
                "opp_move_3": opp_move_3.id if opp_move_3 else None,
                "opp_move_4": opp_move_4.id if opp_move_4 else None,

                # --- Team Data / Available Switches --- #
                "my_switch_1": my_switches[0].species if my_switches[0] else None,
                "my_switch_2": my_switches[1].species if my_switches[1] else None,
                "my_switch_3": my_switches[2].species if my_switches[2] else None,
                "my_switch_4": my_switches[3].species if my_switches[3] else None,
                "my_switch_5": my_switches[4].species if my_switches[4] else None,
                "opp_switch_1": opp_switches[0].species if opp_switches[0] else None,
                "opp_switch_2": opp_switches[1].species if opp_switches[1] else None,
                "opp_switch_3": opp_switches[2].species if opp_switches[2] else None,
                "opp_switch_4": opp_switches[3].species if opp_switches[3] else None,
                "opp_switch_5": opp_switches[4].species if opp_switches[4] else None,

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


# --- Special Case Processing (Poke-env does not see weather/terrain being active on the turn it is set on switch in) --- #

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

weather_seen = {} # Implemented to work around a Poke-env bug where weather start turn is incremented every turn
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


# --- Pokémon processing --- #

def get_atk_boost(pokemon):
    return pokemon.boosts["atk"]

def get_def_boost(pokemon):
    return pokemon.boosts["def"]

def get_spa_boost(pokemon):
    return pokemon.boosts["spa"]

def get_spd_boost(pokemon):
    return pokemon.boosts["spd"]

def get_spe_boost(pokemon):
    return pokemon.boosts["spe"]

EFFECTS = {Effect.ENCORE, Effect.TAUNT, Effect.TRAPPED, Effect.PARTIALLY_TRAPPED, Effect.YAWN, Effect.SUBSTITUTE, Effect.CONFUSION, Effect.LEECH_SEED, Effect.HEAL_BLOCK}

def get_effects(pokemon):
    effect_1 = None
    effect_2 = None

    for effect in pokemon.effects:
        if effect in EFFECTS:
            if effect_1 is None:
                effect_1 = effect
            elif effect_2 is None:
                effect_2 = effect
                break

    return effect_1, effect_2


# --- Moves Processing --- #

def get_move_at_index(pokemon, index):
    moves = []

    for move in pokemon.moves.values():
        moves.append(move)

    if index - 1 < len(moves):
        return moves[index - 1]

    return None

def get_max_power(move):
    if move is None:
        return None

    max_hits = move.n_hit[1]
    power = move.base_power

    return max_hits * power

# BUG: function below does not work as intended; further iteration and testing required
def check_self_boost(move):
    if move is None:
        return None

    if move.self_boost is not None:
        return True

    return False


# --- Team Processing --- #

def safe_my_available_switches(battle, index):
    switches = battle.available_switches

    if len(switches) >= index:
        return switches[index - 1]

    return None

def opp_available_switches(battle, opp_team, index):
    if opp_team is None:
        return None

    switches = []
    for member in opp_team:
        if member.species != battle.opponent_active_pokemon.species and not member.fainted:
            switches.append(member)

    if len(switches) >= index:
        return switches[index - 1]

    return None