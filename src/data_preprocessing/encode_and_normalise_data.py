import pandas as pd
import os
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
import joblib

data = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "..", "data", "data.csv"))

# --- Process Available Actions --- #
available_actions = []
for _, row in data.iterrows():
    actions = []

    for i in range(1, 5):
        move = row[f"my_move_{i}"]
        if move != "none":
            actions.append(move)
            if row["my_can_tera"]:
                actions.append(f"tera_{move}")

    for i in range(1, 6):
        switch = row[f"my_switch_{i}"]
        if switch != "none":
            actions.append(f"switch_{switch}")

    available_actions.append(",".join(actions))

data["available_actions"] = available_actions

# --- Drop columns --- #

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

data["opp_hp"] = data["opp_hp"].round(1)

# --- Encode categorical data --- #
encoders = {}
os.makedirs(os.path.join(os.path.dirname(__file__), "encoders"), exist_ok=True)

for column in data.columns:
    if isinstance(data[column].iloc[0], str) and column != "available_actions":
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
        if column != "action" and column != "available_actions":
            normalise_columns.append(column)

scaler = MinMaxScaler()
data[normalise_columns] = scaler.fit_transform(data[normalise_columns])
joblib.dump(scaler, os.path.join(os.path.dirname(__file__), "encoders", "scaler.pkl"))

# Save data
data.to_csv(os.path.join(os.path.dirname(__file__), "..", "..", "data", "data_processed.csv"), index=False)
print(f"Shape after encoding: {data.shape}")

# --- Train/Test split --- #
training_data, testing_data = train_test_split(data, test_size=0.1, random_state=38)
training_data.to_csv(os.path.join(os.path.dirname(__file__), "..", "..", "data", "training_data.csv"), index=False)
testing_data.to_csv(os.path.join(os.path.dirname(__file__), "..", "..", "data", "testing_data.csv"), index=False)