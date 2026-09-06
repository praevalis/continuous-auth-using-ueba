from copy import deepcopy
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


@dataclass(slots=True)
class AutoencoderTrainingResult:
	model: AutoEncoder
	train_reconstruction_errors: np.ndarray
	val_reconstruction_errors: np.ndarray
	train_loss_history: list[float]
	val_loss_history: list[float]
	selected_epoch: int
	selected_val_loss: float


def compute_reconstruction_errors(
	model: AutoEncoder,
	values: np.ndarray,
	batch_size: int,
) -> np.ndarray:
	device = next(model.parameters()).device
	loader = DataLoader(
		FeatureDataset(values),
		batch_size=batch_size,
		shuffle=False,
	)
	errors: list[np.ndarray] = []
	model.eval()

	with torch.no_grad():
		for batch in loader:
			batch = batch.to(device)
			reconstruction = model(batch)
			batch_errors = ((reconstruction - batch) ** 2).mean(dim=1)
			errors.append(batch_errors.cpu().numpy())

	return np.concatenate(errors) if errors else np.array([], dtype=float)


def train_autoencoder(
	train_values: np.ndarray,
	val_values: np.ndarray,
	config: AutoencoderConfig,
	use_gpu: bool = True,
) -> AutoencoderTrainingResult:
	device = 'cuda' if use_gpu and torch.cuda.is_available() else 'cpu'
	model = AutoEncoder(
		input_dim=train_values.shape[1],
		hidden_dim=config.hidden_dim,
		bottleneck_dim=config.bottleneck_dim,
	).to(device)
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
	best_epoch = 0
	best_val_loss = float('inf')
	best_state: dict[str, torch.Tensor] | None = None

	for epoch in range(config.epochs):
		model.train()
		epoch_train_loss = 0.0

		for batch in train_loader:
			batch = batch.to(device)
			reconstruction = model(batch)
			loss_per_sample = criterion(reconstruction, batch).mean(dim=1)
			loss = loss_per_sample.mean()

			optimizer.zero_grad()
			loss.backward()
			optimizer.step()

			epoch_train_loss += loss.item() * batch.size(0)

		model.eval()
		epoch_val_loss = 0.0

		with torch.no_grad():
			for batch in val_loader:
				batch = batch.to(device)
				reconstruction = model(batch)
				loss_per_sample = criterion(reconstruction, batch).mean(dim=1)
				loss = loss_per_sample.mean()

				epoch_val_loss += loss.item() * batch.size(0)

		epoch_train_loss /= len(train_values)
		epoch_val_loss /= len(val_values)
		train_loss_history.append(epoch_train_loss)
		val_loss_history.append(epoch_val_loss)
		if epoch_val_loss < best_val_loss:
			best_epoch = epoch + 1
			best_val_loss = epoch_val_loss
			best_state = deepcopy(model.state_dict())

		print(
			f'Epoch {epoch + 1}/{config.epochs} | '
			f'Train Loss: {epoch_train_loss:.6f} | '
			f'Val Loss: {epoch_val_loss:.6f}'
		)

	if config.checkpoint_strategy == 'best_validation':
		if best_state is None:
			raise RuntimeError('Training did not produce a validation checkpoint.')
		model.load_state_dict(best_state)
		selected_epoch = best_epoch
		selected_val_loss = best_val_loss
	elif config.checkpoint_strategy == 'last_epoch':
		selected_epoch = len(val_loss_history)
		selected_val_loss = val_loss_history[-1]
	else:
		raise ValueError(
			f'Unsupported checkpoint strategy: {config.checkpoint_strategy}'
		)

	train_reconstruction_errors = compute_reconstruction_errors(
		model,
		train_values,
		config.batch_size,
	)
	val_reconstruction_errors = compute_reconstruction_errors(
		model,
		val_values,
		config.batch_size,
	)

	return AutoencoderTrainingResult(
		model=model,
		train_reconstruction_errors=train_reconstruction_errors,
		val_reconstruction_errors=val_reconstruction_errors,
		train_loss_history=train_loss_history,
		val_loss_history=val_loss_history,
		selected_epoch=selected_epoch,
		selected_val_loss=selected_val_loss,
	)
