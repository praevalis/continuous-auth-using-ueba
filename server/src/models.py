import torch
import pickle
import torch.nn as nn

from src.env import vars

class AutoEncoder(nn.Module):
  def __init__(self, input_dim) -> None:
    super(AutoEncoder, self).__init__()

    self.encoder = nn.Sequential(
        nn.Linear(input_dim, 32),
        nn.ReLU(),
        nn.Linear(32, 64)
    )
    self.decoder = nn.Sequential(
        nn.Linear(64, 32),
        nn.ReLU(),
        nn.Linear(32, input_dim)
    )

  def forward(self, X):
    return self.decoder(self.encoder(X))
  
ae_model = AutoEncoder(vars.AUTOENCODER_INPUT_DIM)
ae_model.load_state_dict(torch.load(f'{vars.ASSETS_DIR}/{vars.AUTOENCODER_PARAMS_PATH}'))
ae_model.eval()

isoforest_model = None
with open(f'{vars.ASSETS_DIR}/{vars.ISOFOREST_PATH}', 'rb') as isf:
    isoforest_model = pickle.load(isf)
    