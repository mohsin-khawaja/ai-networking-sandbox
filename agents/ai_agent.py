"""AI agent for link health prediction using PyTorch."""
import torch
import torch.nn as nn
from typing import Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SimpleHealthModel(nn.Module):
    """A lightweight feedforward model to estimate link health."""
    
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(3, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)


# Initialize model and device
# Note: This uses MPS (Metal Performance Shaders) on Mac for GPU acceleration.
# For CUDA-based environments (Linux/Windows with NVIDIA GPUs), change to:
# device = "cuda" if torch.cuda.is_available() else "cpu"
device = "mps" if torch.backends.mps.is_available() else "cpu"
try:
    model = SimpleHealthModel().to(device)
    model.eval()
    logger.info(f"AI model initialized on device: {device}")
except Exception as e:
    logger.error(f"Failed to initialize AI model on {device}: {e}")
    # Fallback to CPU if device initialization fails
    device = "cpu"
    model = SimpleHealthModel().to(device)
    model.eval()
    logger.info(f"AI model initialized on fallback device: {device}")


def predict_link_health(rx_errors: int, tx_errors: int, utilization: float) -> dict:
    """
    Run AI model to predict overall link health based on telemetry.
    
    Maps to Aviz NCP functionality:
    - Analyzes real-time telemetry from network devices
    - Uses ML model to predict link degradation
    - Provides actionable health scores for monitoring and alerting
    
    Args:
        rx_errors: Number of receive errors
        tx_errors: Number of transmit errors
        utilization: Link utilization (0.0 to 1.0)
        
    Returns:
        Dictionary containing health_score and status
    """
    logger.info(f"Predicting link health: rx_errors={rx_errors}, tx_errors={tx_errors}, utilization={utilization}")
    
    try:
        # Validate inputs
        if not (0.0 <= utilization <= 1.0):
            logger.warning(f"Utilization out of range: {utilization}, clamping to [0, 1]")
            utilization = max(0.0, min(1.0, utilization))
        
        if rx_errors < 0 or tx_errors < 0:
            logger.warning(f"Negative error counts detected, using absolute values")
            rx_errors = abs(rx_errors)
            tx_errors = abs(tx_errors)
        
        with torch.no_grad():
            x = torch.tensor([[rx_errors, tx_errors, utilization]], dtype=torch.float32).to(device)
            score = model(x).item()
        
        result = {
            "health_score": round(score, 3),
            "status": "healthy" if score > 0.7 else "warning",
            "inputs": {
                "rx_errors": rx_errors,
                "tx_errors": tx_errors,
                "utilization": utilization
            }
        }
        
        logger.debug(f"Health prediction: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error during health prediction: {e}")
        return {
            "error": "Prediction failed",
            "message": str(e),
            "health_score": None,
            "status": "error"
        }

