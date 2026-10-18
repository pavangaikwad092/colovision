import cv2
import numpy as np
import torch
from PIL import Image

from ..config import settings
from .architectures import build_segmentation_model


DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

model = None


def load_segmentation_model():
    global model

    path = settings.models_dir / "final_segmentation_model.pth"

    if not path.exists():
        raise RuntimeError(
            f"Segmentation model missing: {path}"
        )

    model = build_segmentation_model()

    checkpoint = torch.load(
        path,
        map_location=DEVICE,
        weights_only=True
    )

    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        model.load_state_dict(
            checkpoint["model_state_dict"]
        )
    else:
        model.load_state_dict(checkpoint)

    model = model.to(DEVICE)
    model.eval()

    print("Segmentation model loaded successfully.")


def preprocess_segmentation(image: Image.Image):

    image = image.convert("RGB")

    image = image.resize(
        (256, 256)
    )

    array = np.asarray(
        image,
        dtype=np.float32
    )

    array = array / 255.0

    mean = np.array(
        [0.485, 0.456, 0.406],
        dtype=np.float32
    )

    std = np.array(
        [0.229, 0.224, 0.225],
        dtype=np.float32
    )

    array = (
        array - mean
    ) / std

    tensor = torch.from_numpy(
        array.transpose(2, 0, 1)
    )

    tensor = tensor.unsqueeze(0)

    return tensor


def predict_segmentation(image: Image.Image):

    if model is None:
        raise RuntimeError(
            "Segmentation model is not loaded."
        )

    original = np.asarray(
        image.convert("RGB")
    )

    tensor = preprocess_segmentation(
        image
    ).to(DEVICE)

    with torch.no_grad():

        output = model(tensor)

    if isinstance(output, (tuple, list)):
        output = output[0]

    probability = torch.sigmoid(
        output
    )[0, 0]

    probability = (
        probability
        .detach()
        .cpu()
        .numpy()
    )

    binary_mask = (
        probability > 0.5
    ).astype(np.uint8) * 255

    binary_mask = cv2.resize(
        binary_mask,
        (
            original.shape[1],
            original.shape[0]
        ),
        interpolation=cv2.INTER_NEAREST
    )

    red_channel = binary_mask
    green_channel = np.zeros_like(
        binary_mask
    )
    blue_channel = np.zeros_like(
        binary_mask
    )

    red_mask = np.dstack(
        [
            red_channel,
            green_channel,
            blue_channel
        ]
    )

    overlay = cv2.addWeighted(
        original,
        0.65,
        red_mask,
        0.35,
        0
    )

    return (
        Image.fromarray(binary_mask),
        Image.fromarray(overlay),
        image.convert("RGB")
    )