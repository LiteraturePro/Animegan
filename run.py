import argparse

import torch
import cv2
import numpy as np
import os

from model import Generator

torch.backends.cudnn.enabled = False
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True
    
def load_image(image_path):
    img = cv2.imread(image_path).astype(np.float32)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img.shape[:2]

    def to_32s(x):
        return 256 if x < 256 else x - x%32

    img = cv2.resize(img, (to_32s(w), to_32s(h)))
    img = torch.from_numpy(img)
    img = img/127.5 - 1.0
    return img


def main():
    device = 'cpu'
    input_dir = './samples/inputs'
    output_dir = './samples/results'

    checkpoint = './models/pytorch_generator_Paprika.pt'
    net = Generator()
    net.load_state_dict(torch.load(checkpoint, map_location="cpu"))
    net.to(device).eval()
    print(f"model loaded: {checkpoint}")
    
    os.makedirs(output_dir, exist_ok=True)

    for image_name in sorted(os.listdir(input_dir)):
        if os.path.splitext(image_name)[-1] not in [".jpg", ".png", ".bmp", ".tiff"]:
            continue
            
        image = load_image(os.path.join(input_dir, image_name))

        with torch.no_grad():
            input = image.permute(2, 0, 1).unsqueeze(0).to(device)
            out = net(input).squeeze(0).permute(1, 2, 0).cpu().numpy()
            out = (out + 1)*127.5
            out = np.clip(out, 0, 255).astype(np.uint8)
            
        cv2.imwrite(os.path.join(output_dir, image_name), cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
        print(f"image saved: {image_name}")

if __name__ == '__main__':
  main()  
