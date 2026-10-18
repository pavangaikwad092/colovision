import numpy as np
import torch

from PIL import Image

from ..config import settings
from .architectures import build_classification_model


DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

CLASSES = [
    "adenocarcinoma",
    "high-grade in",
    "low-grade in",
    "normal",
    "polyp",
    "serrated adenoma"
]

model = None


def load_classification_model():

    global model

    path = (
        settings.models_dir
        / "best_classifier_model_v3.pth"
    )

    if not path.exists():
        raise RuntimeError(
            f"Classification model missing: {path}"
        )

    model = build_classification_model()

    checkpoint = torch.load(
        path,
        map_location=DEVICE,
        weights_only=False
    )

    if (
        isinstance(checkpoint, dict)
        and "model_state_dict" in checkpoint
    ):

        model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        if "class_names" in checkpoint:

            saved_classes = list(
                checkpoint["class_names"]
            )

            if len(saved_classes) == 6:
                CLASSES[:] = [
                    str(x)
                    for x in saved_classes
                ]

    else:

        model.load_state_dict(
            checkpoint
        )

    model = model.to(DEVICE)

    model.eval()

    print(
        "Classification model loaded successfully."
    )

    print(
        "Classes:",
        CLASSES
    )


def preprocess_classification(
    image: Image.Image
):

    image = image.convert("RGB")

    image = image.resize(
        (224, 224)
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


def predict_classification(
    image: Image.Image
):

    if model is None:
        raise RuntimeError(
            "Classification model is not loaded."
        )

    tensor = preprocess_classification(
        image
    ).to(DEVICE)

    with torch.no_grad():

        outputs = model(
            tensor
        )

        probabilities = torch.softmax(
            outputs,
            dim=1
        )[0]

    probabilities = (
        probabilities
        .detach()
        .cpu()
        .numpy()
    )

    predicted_index = int(
        np.argmax(probabilities)
    )

    confidence = float(
        probabilities[predicted_index]
    )

    probability_list = [
        float(x)
        for x in probabilities
    ]

    return {
        "predicted_class":
            CLASSES[predicted_index],

        "confidence":
            confidence,

        "probabilities":
            probability_list
    }