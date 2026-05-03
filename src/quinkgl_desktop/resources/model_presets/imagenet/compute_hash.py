from peer_script import ImageNet1kNet
from quinkgl.manifest import compute_arch_hash


if __name__ == "__main__":
    print(compute_arch_hash(ImageNet1kNet()))
