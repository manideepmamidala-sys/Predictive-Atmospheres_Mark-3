import numpy as np
import torch

from src.services.container import ServiceContainer
from src.services.orchestrator import NeuroArchitectureOrchestrator


class DummyModel(torch.nn.Module):
    def forward(self, x):
        batch = x.shape[0]
        out = torch.zeros((batch, 2), dtype=torch.float32)
        out[:, 0] = 0.2
        out[:, 1] = 0.1
        return out


def test_service_container_updates_services_model_reference():
    services = ServiceContainer(model=DummyModel())

    pred_1 = services.prediction_service.predict(10.0, 8.0, 3.5)
    assert -1.0 <= pred_1.valence <= 1.0

    replacement_model = DummyModel()
    services.set_model(replacement_model)

    assert services.prediction_service._model is replacement_model
    assert services.optimization_service._prediction_service._model is replacement_model


def test_orchestrator_analyze_and_optimize_runs():
    services = ServiceContainer(model=DummyModel())
    orchestrator = NeuroArchitectureOrchestrator(services)

    eeg_signal = np.random.randn(3, 60 * 256)
    result = orchestrator.analyze_and_optimize(eeg_signal=eeg_signal, fs=256, target_score=0.6)

    assert result.optimized_room.length >= 2.0
    assert result.optimized_room.width >= 2.0
    assert result.optimized_room.height >= 2.5
    assert -1.0 <= result.optimized_prediction.valence <= 1.0
