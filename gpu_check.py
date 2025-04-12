#!/usr/bin/env python3

def check_tensorflow_gpu():
    try:
        import tensorflow as tf
        gpus = tf.config.list_physical_devices('GPU')
        return len(gpus) > 0
    except:
        return False

def check_pytorch_gpu():
    try:
        import torch
        return torch.cuda.is_available()
    except:
        return False

if __name__ == "__main__":
    # Check if either framework detects a GPU
    has_gpu = check_tensorflow_gpu() or check_pytorch_gpu()
    print(has_gpu)
