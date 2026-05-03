from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ManifestPreset:
    key: str
    label: str
    description: str
    name: str
    task_type: str
    input_shape: str
    output_shape: str
    label_type: str
    output_path: str


MANIFEST_PRESETS = [
    ManifestPreset("cifar10", "CIFAR-10", "Image classification, 10 classes", "cifar10-swarm", "class", "3,32,32", "10", "integer", "cifar10.qgl"),
    ManifestPreset("mnist", "MNIST", "Digit recognition, 28x28 grayscale", "mnist-swarm", "class", "1,28,28", "10", "integer", "mnist.qgl"),
    ManifestPreset("imagenet", "ImageNet-1k", "Large-scale image classification", "imagenet-swarm", "class", "3,224,224", "1000", "integer", "imagenet.qgl"),
    ManifestPreset("custom", "Custom", "Start from a blank manifest", "custom-swarm", "class", "", "", "integer", "custom.qgl"),
]

PRESET_BY_LABEL = {preset.label: preset for preset in MANIFEST_PRESETS}

