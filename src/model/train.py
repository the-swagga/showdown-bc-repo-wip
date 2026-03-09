import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from bc_model import BCDataset, BCModel

torch.manual_seed(38)

# --- Training Variables --- #
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "training_data.csv")
BATCH_SIZE = 64
EPOCH_NUM = 64
LEARN_RATE = 0.001
VALIDATION_SPLIT = 0.1
PATIENCE = 10

# --- Dataset --- #
dataset = BCDataset(DATA_PATH)

validation_size = int(len(dataset) * VALIDATION_SPLIT)
training_size = len(dataset) - validation_size
training_set, validation_set = random_split(dataset, [training_size, validation_size], generator=torch.Generator().manual_seed(38))

training_loader = DataLoader(training_set, batch_size=BATCH_SIZE, shuffle=True)
validation_loader = DataLoader(validation_set, batch_size=BATCH_SIZE)

# --- Model --- #
input_size = dataset.X.shape[1]
output_size = int(dataset.y.max().item()) + 1
model = BCModel(input_size, output_size)

# --- Train and Save --- #
save_path = os.path.join(os.path.dirname(__file__), "..", "..", "saved_models", "bc_model.pt")
os.makedirs(os.path.dirname(save_path), exist_ok=True)

optimiser = torch.optim.Adam(model.parameters(), lr=LEARN_RATE)
loss_function = nn.CrossEntropyLoss()

best_validation_loss = float("inf")
patience_count = 0

for epoch in range(EPOCH_NUM):
    model.train()
    training_loss = 0

    for X_batch, y_batch in training_loader:
        optimiser.zero_grad()
        predictions = model(X_batch)
        loss = loss_function(predictions, y_batch)
        loss.backward()
        optimiser.step()
        training_loss += loss.item()

    model.eval()
    validation_loss = 0
    correct = 0
    with torch.no_grad():
        for X_batch, y_batch in validation_loader:
            predictions = model(X_batch)
            validation_loss += loss_function(predictions, y_batch).item()
            correct += (predictions.argmax(dim=1) == y_batch).sum().item()

    accuracy = (correct / validation_size) * 100
    print(f"Epoch {epoch + 1}/{EPOCH_NUM} - Train Loss: {training_loss / len(training_loader):.4f} - Val Loss: {validation_loss / len(validation_loader):.4f} - Val Accuracy: {accuracy:.1f}%")

    if validation_loss < best_validation_loss:
        best_validation_loss = validation_loss
        torch.save(model.state_dict(), save_path)
        patience_count = 0
    else:
        patience_count += 1
        if patience_count >= PATIENCE:
            break

torch.save(model.state_dict(), save_path)
print(f"Model saved to {save_path}")
