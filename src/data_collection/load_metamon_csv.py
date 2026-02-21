from datasets import load_dataset, concatenate_datasets

dataset_path = "jakegrigsby/metamon-raw-replays"
split_data = load_dataset(dataset_path)

splits = []
for split in split_data.keys():
    splits.append(split_data[split])

data = concatenate_datasets(splits)

df = data.to_pandas()
df.to_csv("metamon_replays.csv", index=False)

print("load_metamon_csv.py DONE")