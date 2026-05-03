import importlib.util

from quinkgl_desktop.services.model_preset_service import ModelPresetService


def test_installs_embedded_preset_files_without_overwriting(tmp_path):
    service = ModelPresetService()
    (tmp_path / "peer_script.py").write_text("existing", encoding="utf-8")

    result = service.install_preset("cifar10", tmp_path)

    assert result.installed["peer_script.py"] == "backed-up"
    assert result.installed["compute_hash.py"] == "written"
    assert (tmp_path / "peer_script.py.bak").read_text(encoding="utf-8") == "existing"
    assert "class Cifar10Net" in (tmp_path / "peer_script.py").read_text(encoding="utf-8")
    assert "compute_arch_hash" in (tmp_path / "compute_hash.py").read_text(encoding="utf-8")


def test_installs_all_manifest_presets(tmp_path):
    service = ModelPresetService()

    for preset in ["cifar10", "mnist", "imagenet"]:
        workspace = tmp_path / preset
        workspace.mkdir()
        result = service.install_preset(preset, workspace)

        assert result.ok is True
        assert (workspace / "peer_script.py").exists()
        assert (workspace / "compute_hash.py").exists()


def test_embedded_preset_scripts_generate_data_when_missing():
    service = ModelPresetService()

    for preset in ["cifar10", "mnist", "imagenet"]:
        script = (service._preset_dir(preset) / "peer_script.py").read_text(encoding="utf-8")

        assert "_ensure_data" in script
        assert "_fallback_tensor_pair" in script
        assert "train.pt" in script
        assert "val.pt" in script

    assert "download=True" in (service._preset_dir("cifar10") / "peer_script.py").read_text(encoding="utf-8")
    assert "download=True" in (service._preset_dir("mnist") / "peer_script.py").read_text(encoding="utf-8")
    assert "FakeData" in (service._preset_dir("imagenet") / "peer_script.py").read_text(encoding="utf-8")


def test_cifar_preset_uses_fallback_tensors_when_download_fails(tmp_path, monkeypatch):
    service = ModelPresetService()
    script_path = service._preset_dir("cifar10") / "peer_script.py"
    spec = importlib.util.spec_from_file_location("cifar10_peer_script_test", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def fail_download(*args, **kwargs):
        raise RuntimeError("download unavailable")

    monkeypatch.setattr(module.datasets, "CIFAR10", fail_download)

    loaders = module.build_loaders(None, data_root=str(tmp_path / "data"), peer_index=1, batch_size=8)

    assert (tmp_path / "data/peer_1/train.pt").exists()
    assert (tmp_path / "data/peer_1/val.pt").exists()
    train_batch = next(iter(loaders[0]))
    assert train_batch[0].shape == (8, 3, 32, 32)


def test_compute_hash_parses_sha256_from_runner(tmp_path):
    calls = []

    def fake_runner(command, cwd, env):
        calls.append((command, cwd, env))
        return 0, "debug\nsha256:" + "a" * 64 + "\n", ""

    service = ModelPresetService(runner=fake_runner)
    (tmp_path / "compute_hash.py").write_text("print('hash')", encoding="utf-8")

    result = service.compute_hash(tmp_path, python_binary="python3", env={"PYTHONPATH": "src"})

    assert result.ok is True
    assert result.hash_value == "sha256:" + "a" * 64
    assert calls == [(["python3", "compute_hash.py"], tmp_path, {"PYTHONPATH": "src"})]
