import os
import torch
from PIL import Image
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

def enhance_image(input_path):
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
    upsampler = RealESRGANer(
        scale=4,
        model_path='weights/RealESRGAN_x4plus.pth',  # Make sure weights exist here
        model=model,
        tile=0,
        tile_pad=10,
        pre_pad=0,
        half=False
    )

    img = Image.open(input_path).convert("RGB")
    img = np.array(img)

    output, _ = upsampler.enhance(img, outscale=4)
    output_img = Image.fromarray(output)

    output_path = "enhanced.jpg"
    output_img.save(output_path)
    return output_path
