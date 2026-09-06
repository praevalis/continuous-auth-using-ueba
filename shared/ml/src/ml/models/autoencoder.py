import torch
from torch import nn


class AutoEncoder(nn.Module):
	def __init__(
		self,
		input_dim: int,
		hidden_dim: int | None = None,
		bottleneck_dim: int | None = None,
	) -> None:
		super().__init__()

		self.input_dim = input_dim
		self.hidden_dim = max(input_dim // 2, 1) if hidden_dim is None else hidden_dim
		self.bottleneck_dim = (
			max(input_dim // 4, 1) if bottleneck_dim is None else bottleneck_dim
		)
		if self.hidden_dim <= 0 or self.bottleneck_dim <= 0:
			raise ValueError('AutoEncoder dimensions must be positive.')
		if self.hidden_dim >= input_dim:
			raise ValueError('AutoEncoder hidden dimension must be less than input.')
		if self.bottleneck_dim >= self.hidden_dim:
			raise ValueError(
				'AutoEncoder bottleneck dimension must be less than hidden dimension.'
			)

		self.encoder = nn.Sequential(
			nn.Linear(input_dim, self.hidden_dim),
			nn.ReLU(),
			nn.Linear(self.hidden_dim, self.bottleneck_dim),
		)
		self.decoder = nn.Sequential(
			nn.Linear(self.bottleneck_dim, self.hidden_dim),
			nn.ReLU(),
			nn.Linear(self.hidden_dim, input_dim),
		)

	def forward(self, values: torch.Tensor) -> torch.Tensor:
		return self.decoder(self.encoder(values))
