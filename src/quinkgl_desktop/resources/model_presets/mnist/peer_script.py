from __future__ import annotations

from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset, random_split
from torchvision import datasets, transforms


class MnistNet(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Flatten(),
            nn.Linear(28 * 28, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 10),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def _load_tensor_pair(path: Path) -> TensorDataset:
    blob = torch.load(path, weights_only=True)
    return TensorDataset(blob["x"], blob["y"])


def _save_split(dataset, path: Path, limit: int) -> None:
    xs = []
    ys = []
    for index in range(min(limit, len(dataset))):
        x, y = dataset[index]
        xs.append(x)
        ys.append(int(y))
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"x": torch.stack(xs), "y": torch.tensor(ys, dtype=torch.long)}, path)


def _fallback_tensor_pair(count: int, shape: tuple[int, ...], classes: int, seed: int) -> TensorDataset:
    generator = torch.Generator().manual_seed(seed)
    x = torch.rand((count, *shape), generator=generator)
    y = torch.arange(count, dtype=torch.long) % classes
    return TensorDataset(x, y)


def _split_lengths(total: int, parts: int) -> list[int]:
    base = total // parts
    remainder = total % parts
    return [base + (1 if index < remainder else 0) for index in range(parts)]


def _ensure_data(data_root: Path, peer_index: int, peers: int = 1) -> None:
    peer_dir = data_root / f"peer_{peer_index}"
    train_path = peer_dir / "train.pt"
    val_path = peer_dir / "val.pt"
    if train_path.exists() and val_path.exists():
        return

    raw_root = data_root / "_torchvision"
    transform = transforms.Compose([transforms.ToTensor()])
    selected = max(0, min(peer_index - 1, peers - 1))
    try:
        full_train = datasets.MNIST(raw_root, train=True, download=True, transform=transform)
        full_val = datasets.MNIST(raw_root, train=False, download=True, transform=transform)
        train_parts = random_split(full_train, _split_lengths(len(full_train), peers), generator=torch.Generator().manual_seed(13))
        val_parts = random_split(full_val, _split_lengths(len(full_val), peers), generator=torch.Generator().manual_seed(17))
        train_ds = train_parts[selected]
        val_ds = val_parts[selected]
    except Exception as exc:
        print(f"MNIST download failed ({exc}); generating local fallback tensors.")
        train_ds = _fallback_tensor_pair(512, (1, 28, 28), 10, seed=1300 + peer_index)
        val_ds = _fallback_tensor_pair(128, (1, 28, 28), 10, seed=1700 + peer_index)

    _save_split(train_ds, train_path, limit=512)
    _save_split(val_ds, val_path, limit=128)


def build_model(manifest, **kwargs):
    return MnistNet()


def build_loaders(manifest, **kwargs):
    data_root = Path(kwargs.get("data_root", "./data")).expanduser().resolve()
    peer_index = int(kwargs.get("peer_index", 1))
    peers = int(kwargs.get("peers", 1))
    batch_size = int(kwargs.get("batch_size", 32))
    _ensure_data(data_root, peer_index, peers=peers)
    peer_dir = data_root / f"peer_{peer_index}"
    train_ds = _load_tensor_pair(peer_dir / "train.pt")
    val_ds = _load_tensor_pair(peer_dir / "val.pt")
    return (
        DataLoader(train_ds, batch_size=batch_size, shuffle=True),
        DataLoader(val_ds, batch_size=batch_size, shuffle=False),
    )


def build_optimizer(manifest, model):
    inner = getattr(model, "model", model)
    return torch.optim.Adam(inner.parameters(), lr=0.001)
