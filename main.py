from src.data_preprocessing.encode_and_normalise_data import preprocess_data
from src.model.train import train_model
from src.model.quant_eval import quantitative_evaluate_model

# This main.py file is for model training and evaluation; for data collection, go to /src/data_collection/poke_env_main.py

def preprocess_train_evaluate(seed=38, records=0, show_loss=True):
    preprocess_data(seed=seed, records=records)
    train_model(seed=seed, show_loss=show_loss)
    quantitative_evaluate_model()
    print()

preprocess_train_evaluate(seed=38, show_loss=False)


