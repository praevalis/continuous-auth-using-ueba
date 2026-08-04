import torch
from torch import nn


class AutoEncoder(nn.Module):
	def __init__(self, input_dim: int) -> None:
		super().__init__()

		hidden_dim = max(input_dim // 2, 1)
		bottleneck_dim = max(input_dim // 4, 1)

		self.encoder = nn.Sequential(
			nn.Linear(input_dim, hidden_dim),
			nn.ReLU(),
			nn.Linear(hidden_dim, bottleneck_dim),
		)
		self.decoder = nn.Sequential(
			nn.Linear(bottleneck_dim, hidden_dim),
			nn.ReLU(),
			nn.Linear(hidden_dim, input_dim),
		)

	def forward(self, values: torch.Tensor) -> torch.Tensor:
		return self.decoder(self.encoder(values))
