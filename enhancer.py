import os
from realesrgan import RealESRGAN
from PIL import Image
import torch

def enhance_image(input_path, output_path):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    image = Image.open(input_path).convert("RGB")

    model = RealESRGAN(device, scale=4)
    model.load_weights('weights/RealESRGAN_x4.pth', download=True)

    sr_image = model.predict(image)
    sr_image.save(output_path)
