import timm
import segmentation_models_pytorch as smp


def build_segmentation_model():
    model = smp.Unet(
        encoder_name="resnet34",
        encoder_weights=None,
        in_channels=3,
        classes=1,
        activation=None
    )

    return model


def build_classification_model():
    model = timm.create_model(
        "efficientnet_b0",
        pretrained=False,
        num_classes=6
    )

    return model