import torch
import pickle
import pandas as pd

from src.env import vars
from src.models import ae_model, isoforest_model

USER_HIST_MAP = {
    'U1': {
        'login_frequency': 3296.0,
        'time_since_last_login': 0.0,
        'avg_inter_event_time': 23.56682,
        'unique_hosts': 12,
        'host_entropy': 2.978570,
        'top_host_ratio': 0.211982,
        'degree_centrality': 0.001451
    },
    'U2': {
        'login_frequency': 1.0,
        'time_since_last_login': 0.0,
        'avg_inter_event_time': 75.338235,
        'unique_hosts': 2,
        'host_entropy': 0.908178,
        'top_host_ratio': 0.676471,
        'degree_centrality': 0.000242
    },
    'U3': {
        'login_frequency': 1.0,
        'time_since_last_login': 0.0,
        'avg_inter_event_time': 61.458824,
        'unique_hosts': 4,
        'host_entropy': 1.197341,
        'top_host_ratio': 0.694118,
        'degree_centrality': 0.000484
    },
    'U4': {
        'login_frequency': 1.0,
        'time_since_last_login': 0.0,
        'avg_inter_event_time': 14.652893,
        'unique_hosts': 2,
        'host_entropy': 0.829313,
        'top_host_ratio': 0.738292,
        'degree_centrality': 0.000242
    }
}

AUTOENCODER_FEATURES = ['unique_hosts', 'host_entropy', 'top_host_ratio', 'degree_centrality', 'hour_of_day', 'day_of_week']
ISOFOREST_FEATURES = ['login_frequency', 'avg_inter_event_time', 'time_since_last_login']

global_scaler, user_scaler = None, None

with open(f'{vars.ASSETS_DIR}/{vars.GLOBAL_SCALER_PATH}', 'rb') as gsf:
    global_scaler = pickle.load(gsf)

with open(f'{vars.ASSETS_DIR}/{vars.USER_SCALER_PATH}', 'rb') as usf:
    user_scaler = pickle.load(usf)

def generate_features(user: str, computer: str, timestamp: int) -> pd.DataFrame:
    features = USER_HIST_MAP[user]
    features['user'] = user
    features['computer'] = computer
    features['timestamp'] = timestamp

    df = pd.DataFrame(features, index=[0])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', origin='2014-01-01')
    df['hour_of_day'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.dayofweek

    return df

def process_input(df: pd.DataFrame) -> tuple[torch.Tensor, torch.Tensor]:
    x_global = df[AUTOENCODER_FEATURES]
    x_user = df[ISOFOREST_FEATURES]

    x_global_scaled = global_scaler.transform(x_global) # type: ignore
    x_user_scaled = user_scaler.transform(x_user) # type: ignore

    x_global_tensor = torch.tensor(x_global_scaled, dtype=torch.float32)
    x_user_tensor = torch.tensor(x_user_scaled, dtype=torch.float32)

    return x_global_tensor, x_user_tensor

def predict(x_global_tensor: torch.Tensor, x_user_tensor: torch.Tensor) -> float:
    recon_error = None
    with torch.no_grad():
        recon = ae_model(x_global_tensor)
        recon_error = torch.mean((x_global_tensor - recon)**2, dim=1).cpu().numpy().flatten()[0]

    anomaly_score = isoforest_model.predict(x_user_tensor)

    alpha = vars.ALPHA
    final_score = alpha * anomaly_score + (1 - alpha) * recon_error

    return final_score