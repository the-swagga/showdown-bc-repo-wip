import pandas as pd
import os
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import joblib

data = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "..", "data", "data.csv"))

drop_columns = [
    "turn",

    # The team runs no screen moves
    "my_side_light_screen", "my_side_reflect", "my_side_aurora_veil",

    # The team only runs stealth rock for hazard moves
    "opp_side_spikes", "opp_side_toxic_spikes", "opp_side_sticky_web",

    # The team runs no protect moves
    "my_turns_protect",

    # EDA found that these are too rare
    "my_effect_2", "opp_effect_2",

    # All moves on the team have 100% accuracy
    "my_move_1_accuracy", "my_move_2_accuracy", "my_move_3_accuracy", "my_move_4_accuracy",

    # Opponent's 3rd move, 4th move, and ability are too rarely known
    "opp_move_3", "opp_move_4", "opp_ability"
]

data.drop(columns=drop_columns, inplace=True)

# Round opponent HP to be consistent with my HP
data["opp_hp"] = data["opp_hp"].round(1)

# --- Encode categorical data --- #
encoders = {}
os.makedirs(os.path.join(os.path.dirname(__file__), "encoders"), exist_ok=True)

for column in data.columns:
    if isinstance(data[column].iloc[0], str):
        label_encoder = LabelEncoder()
        data[column] = label_encoder.fit_transform(data[column].astype(str))
        encoders[column] = label_encoder
        joblib.dump(encoders[column], os.path.join(os.path.dirname(__file__), "encoders", f"{column}.pkl"))

for column in data.columns:
    if data[column].dtype == "bool":
        data[column] = data[column].astype(int)

# --- Normalise data --- #
normalise_columns = []
for column in data.columns:
    if data[column].dtype == "float64" or data[column].dtype == "int64":
        if column != "action":
            normalise_columns.append(column)

scaler = MinMaxScaler()
data[normalise_columns] = scaler.fit_transform(data[normalise_columns])
joblib.dump(scaler, os.path.join(os.path.dirname(__file__), "encoders", "scaler.pkl"))

# Save data
data.to_csv(os.path.join(os.path.dirname(__file__), "..", "..", "data", "data_encoded.csv"), index=False)
print(f"Shape after encoding: {data.shape}")