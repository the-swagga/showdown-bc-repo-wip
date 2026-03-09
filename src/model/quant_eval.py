import os
import torch
import pandas as pd
import joblib
from bc_model import BCModel

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "testing_data.csv")
ENCODERS_PATH = os.path.join(os.path.dirname(__file__), "..", "data_preprocessing", "encoders")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "saved_models", "bc_model.pt")

def quantitative_evaluate_model():
    data = pd.read_csv(DATA_PATH)
    action_encoder = joblib.load(os.path.join(ENCODERS_PATH, "action.pkl"))

    X = torch.tensor(data.drop(columns=["action", "available_actions"]).values, dtype=torch.float32)
    y = torch.tensor(data["action"].values, dtype=torch.long)

    input_size = X.shape[1]
    output_size = len(action_encoder.classes_)
    model = BCModel(input_size, output_size)
    model.load_state_dict(torch.load(MODEL_PATH))
    model.eval()

    correct_raw = 0
    correct_masked = 0

    with torch.no_grad():
        for i in range(len(X)):
            logits = model(X[i].unsqueeze(0)).squeeze(0)

            if logits.argmax().item() == y[i].item():
                correct_raw += 1

            available = data.iloc[i]["available_actions"].split(",")
            mask = torch.full(logits.shape, float("-inf"))
            for action in available:
                if action in action_encoder.classes_:
                    index = action_encoder.transform([action])[0]
                    mask[index] = 0

            if (logits + mask).argmax().item() == y[i].item():
                correct_masked += 1

    total_actions = len(X)
    raw_accuracy = (correct_raw / total_actions) * 100
    masked_accuracy = (correct_masked / total_actions) * 100

    above_random = []
    for i in range(total_actions):
        n = len(data.iloc[i]["available_actions"].split(","))
        above_random.append((1 / n) * 100)
    avg_acc_above_random = masked_accuracy - (sum(above_random) / len(above_random))

    print(f"Raw Accuracy: {raw_accuracy:.1f}%")
    print(f"Masked Accuracy: {masked_accuracy:.1f}%")
    print(f"Average Accuracy Above Random: {avg_acc_above_random:.1f}%")