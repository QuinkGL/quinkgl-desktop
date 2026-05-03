from peer_script import Cifar10Net
from quinkgl.manifest import compute_arch_hash


if __name__ == "__main__":
    print(compute_arch_hash(Cifar10Net()))
