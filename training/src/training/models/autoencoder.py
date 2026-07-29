from dataclasses import dataclass

import numpy as np
import torch
from torch import nn, optim
from torch.utils.data import DataLoader, Dataset

from training.config import AutoencoderConfig


class FeatureDataset(Dataset):
	def __init__(self, values: np.ndarray) -> None:
		self.values = torch.tensor(values, dtype=torch.float32)

	def __len__(self) -> int:
		return len(self.values)

	def __getitem__(self, index: int) -> torch.Tensor:
		return self.values[index]


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


@dataclass(slots=True)
class AutoencoderTrainingResult:
	model: AutoEncoder
	train_reconstruction_errors: np.ndarray
	val_reconstruction_errors: np.ndarray
	train_loss_history: list[float]
	val_loss_history: list[float]


def train_autoencoder(
	train_values: np.ndarray,
	val_values: np.ndarray,
	config: AutoencoderConfig,
	use_gpu: bool = True,
) -> AutoencoderTrainingResult:
	device = 'cuda' if use_gpu and torch.cuda.is_available() else 'cpu'
	model = AutoEncoder(input_dim=train_values.shape[1]).to(device)
	criterion = nn.MSELoss(reduction='none')
	optimizer = optim.Adam(model.parameters(), lr=config.learning_rate)

	train_loader = DataLoader(
		FeatureDataset(train_values),
		batch_size=config.batch_size,
		shuffle=True,
	)
	val_loader = DataLoader(
		FeatureDataset(val_values),
		batch_size=config.batch_size,
		shuffle=False,
	)

	train_loss_history: list[float] = []
	val_loss_history: list[float] = []
	latest_train_errors = np.array([], dtype=float)
	latest_val_errors = np.array([], dtype=float)

	for epoch in range(config.epochs):
		model.train()
		epoch_train_loss = 0.0
		epoch_train_errors: list[np.ndarray] = []

		for batch in train_loader:
			batch = batch.to(device)
			reconstruction = model(batch)
			loss_per_sample = criterion(reconstruction, batch).mean(dim=1)
			loss = loss_per_sample.mean()

			optimizer.zero_grad()
			loss.backward()
			optimizer.step()

			epoch_train_loss += loss.item() * batch.size(0)
			epoch_train_errors.append(loss_per_sample.detach().cpu().numpy())

		model.eval()
		epoch_val_loss = 0.0
		epoch_val_errors: list[np.ndarray] = []

		with torch.no_grad():
			for batch in val_loader:
				batch = batch.to(device)
				reconstruction = model(batch)
				loss_per_sample = criterion(reconstruction, batch).mean(dim=1)
				loss = loss_per_sample.mean()

				epoch_val_loss += loss.item() * batch.size(0)
				epoch_val_errors.append(loss_per_sample.cpu().numpy())

		epoch_train_loss /= len(train_values)
		epoch_val_loss /= len(val_values)
		train_loss_history.append(epoch_train_loss)
		val_loss_history.append(epoch_val_loss)
		latest_train_errors = np.concatenate(epoch_train_errors)
		latest_val_errors = np.concatenate(epoch_val_errors)

		print(
			f'Epoch {epoch + 1}/{config.epochs} | '
			f'Train Loss: {epoch_train_loss:.6f} | '
			f'Val Loss: {epoch_val_loss:.6f}'
		)

	return AutoencoderTrainingResult(
		model=model,
		train_reconstruction_errors=latest_train_errors,
		val_reconstruction_errors=latest_val_errors,
		train_loss_history=train_loss_history,
		val_loss_history=val_loss_history,
	)
