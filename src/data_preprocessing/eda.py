import pandas as pd
import matplotlib.pyplot as plt
import os

data = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "..", "data", "data.csv"))

action_counts = data["action"].value_counts()
plt.figure(figsize=(6, 10))
plt.barh(action_counts.index, action_counts.values, color="blue")
plt.xlabel("Count")
plt.tight_layout()
plt.show()

opp_pokemon_counts = data["opp_pokemon"].value_counts()
plt.figure(figsize=(8, 12))
plt.barh(opp_pokemon_counts.index, opp_pokemon_counts.values, color="blue")
plt.xlabel("Count")
plt.tight_layout()
plt.show()

status_counts = data[data["my_status"] != "none"]["my_status"].value_counts()
plt.figure(figsize=(6, 10))
plt.barh(status_counts.index, status_counts.values, color="blue")
plt.xlabel("Count")
plt.tight_layout()
plt.show()

print()
print(f"Shape: {data.shape}")
print()
print(f"Empty data: {data.isnull().sum().sum()}")
print()

for column in data.columns:
    print(f"{column}: {data[column].nunique()} unique values")
print()

print(f"Opponent ability unknown: {(data['opp_ability'] == 'unknown').sum() / len(data) * 100:.1f}%")
print()

for col in ["opp_move_1", "opp_move_2", "opp_move_3", "opp_move_4"]:
    unknown_pct = (data[col] == "unknown").sum() / len(data) * 100
    print(f"{col}: {unknown_pct:.1f}% unknown")
print()

# drop my screens, opp spikes, opp tox spikes, opp sticky web, my protect, my effect 2, opp effect 2, my move accuracy
# Round opp hp to 1 decimal place
# maybe drop opp moves 3 and 4