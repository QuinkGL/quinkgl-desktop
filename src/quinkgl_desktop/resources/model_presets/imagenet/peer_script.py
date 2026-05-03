from __future__ import annotations

from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset, random_split
from torchvision import datasets, transforms


class ImageNet1kNet(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(3, stride=2, padding=1),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = nn.Linear(64, 1000)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        return self.classifier(torch.flatten(x, 1))


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

    transform = transforms.Compose([transforms.ToTensor()])
    selected = max(0, min(peer_index - 1, peers - 1))
    try:
        full_train = datasets.FakeData(size=1024, image_size=(3, 224, 224), num_classes=1000, transform=transform, random_offset=0)
        full_val = datasets.FakeData(size=256, image_size=(3, 224, 224), num_classes=1000, transform=transform, random_offset=10_000)
        train_parts = random_split(full_train, _split_lengths(len(full_train), peers), generator=torch.Generator().manual_seed(13))
        val_parts = random_split(full_val, _split_lengths(len(full_val), peers), generator=torch.Generator().manual_seed(17))
        train_ds = train_parts[selected]
        val_ds = val_parts[selected]
    except Exception as exc:
        print(f"ImageNet-1k fallback dataset failed ({exc}); generating local tensors.")
        train_ds = _fallback_tensor_pair(128, (3, 224, 224), 1000, seed=1300 + peer_index)
        val_ds = _fallback_tensor_pair(32, (3, 224, 224), 1000, seed=1700 + peer_index)

    _save_split(train_ds, train_path, limit=128)
    _save_split(val_ds, val_path, limit=32)


def build_model(manifest, **kwargs):
    return ImageNet1kNet()


def build_loaders(manifest, **kwargs):
    data_root = Path(kwargs.get("data_root", "./data")).expanduser().resolve()
    peer_index = int(kwargs.get("peer_index", 1))
    peers = int(kwargs.get("peers", 1))
    batch_size = int(kwargs.get("batch_size", 16))
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
    return torch.optim.SGD(inner.parameters(), lr=0.005, momentum=0.9)
