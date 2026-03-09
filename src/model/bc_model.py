import pandas as pd
import torch
from torch.utils.data import Dataset
import torch.nn as nn

class BCDataset(Dataset):
    def __init__(self, path):
        data = pd.read_csv(path)
        self.X = torch.tensor(data.drop(columns=["action", "available_actions"]).values, dtype=torch.float32)
        self.y = torch.tensor(data["action"].values, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, index):
        return self.X[index], self.y[index]

class BCModel(nn.Module):
    def __init__(self, input_size, output_size):
        super().__init__()

        self.dropout = nn.Dropout(0.2)
        self.relu = nn.ReLU()

        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_size)

    def forward(self, x):
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.dropout(self.relu(self.fc2(x)))
        x = self.fc3(x)

        return x