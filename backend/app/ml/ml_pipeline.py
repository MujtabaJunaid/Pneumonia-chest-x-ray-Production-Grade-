"""
Ù¾Ø§Ø¦Ù„Ù…ÙˆÙ†ÛŒØ§ Ú©ÛŒ ØªØ´Ø®ÛŒØµ Ú©Û’ Ù„ÛŒÛ’ ONNX Ø±Ù† Ù¹Ø§Ø¦Ù… Ø§ÙˆØ± PyTorch Ù…Ø§ÚˆÙ„
Pneumonia Detection ML Pipeline - ONNX Runtime and PyTorch Models
"""

import numpy as np
import torch
import torchvision.models as models
from torch import nn
from typing import Dict, Tuple, Optional, Union
import onnxruntime as ort
from PIL import Image
import time
import os
from pathlib import Path

try:
    import pydicom
    from pydicom.pixel_data_handlers.numpy_handler import apply_modality_lut
except ImportError:
    pydicom = None


class PneumoniaModel(nn.Module):
    """
    EfficientNetB0 Ù¾Ø± Ù…Ø¨Ù†ÛŒ Ù¾Ø§Ø¦Ù„Ù…ÙˆÙ†ÛŒØ§ Ú©ÛŒ ØªØ´Ø®ÛŒØµ Ú©Ø§ Ù…Ø§ÚˆÙ„
    Ù…Ø§ÚˆÙ„ Ú©ÛŒ Ø¢Ø®Ø±ÛŒ ØªÛÛ Ù…ÛŒÚº 2 Ú©Ù„Ø§Ø³ (Ù†Ø§Ø±Ù…Ù„/Ù†Ù…ÙˆÙ†ÛŒØ§) Ú©ÛŒ ØªØ¨Ø¯ÛŒÙ„ÛŒ Ú©Û’ Ø³Ø§ØªÚ¾
    """

    def __init__(self, num_classes: int = 2):
        """
        Ù…Ø§ÚˆÙ„ Ú©Ùˆ Ø´Ø±ÙˆØ¹ Ú©Ø±ÛŒÚº
        
        Parameters:
        -----------
        num_classes : int
            ØªØ´Ø®ÛŒØµ Ú©ÛŒ Ú©Ù„Ø§Ø³Ø² Ú©ÛŒ ØªØ¹Ø¯Ø§Ø¯ (ÚˆÛŒÙØ§Ù„Ù¹: 2)
        """
        super(PneumoniaModel, self).__init__()
        
        print("ðŸ“¦ EfficientNetB0 Ù…Ø§ÚˆÙ„ Ù„ÙˆÚˆ Ú©ÛŒØ§ Ø¬Ø§ Ø±ÛØ§ ÛÛ’...")
        # Pre-trained EfficientNetB0 Ù„ÙˆÚˆ Ú©Ø±ÛŒÚº
        self.model = models.efficientnet_b0(pretrained=True)
        
        # Ø¢Ø®Ø±ÛŒ Ú©Ù„Ø§Ø³ÛŒÙØ§Ø¦Ø± ØªÛÛ Ú©Ùˆ 2 Ú©Ù„Ø§Ø³ Ú©Û’ Ù„ÛŒÛ’ ØªØ¨Ø¯ÛŒÙ„ Ú©Ø±ÛŒÚº
        num_features = self.model.classifier[1].in_features
        self.model.classifier[1] = nn.Linear(num_features, num_classes)
        
        print(f"âœ“ Ù…Ø§ÚˆÙ„ Ú©Ùˆ {num_classes} Ú©Ù„Ø§Ø³Ø² Ú©Û’ Ø³Ø§ØªÚ¾ ØªÛŒØ§Ø± Ú©ÛŒØ§ Ú¯ÛŒØ§")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        ØªÙ†Ø¨Û Ø¯ÛŒÚº (Forward pass)
        
        Parameters:
        -----------
        x : torch.Tensor
            Ø§Ù† Ù¾Ù¹ Ù¹ÛŒÙ†Ø³Ø± Ø´Ú©Ù„ (batch, 3, 224, 224)
        
        Returns:
        --------
        torch.Tensor
            Ø¢Ø¤Ù¹ Ù¾Ù¹ ØªÙ†Ø¨ÛØ§Øª
        """
        return self.model(x)


def load_weights(model: PneumoniaModel, model_path: str) -> None:
    """
    Ù…Ø§ÚˆÙ„ Ú©Û’ ÙˆØ²Ù† Ù„ÙˆÚˆ Ú©Ø±ÛŒÚº
    
    Parameters:
    -----------
    model : PneumoniaModel
        Ù…Ø§ÚˆÙ„ Ú©ÛŒ Ù…Ø«Ø§Ù„
    model_path : str
        .pth ÙØ§Ø¦Ù„ Ú©Ø§ Ø±Ø§Ø³ØªÛ
    """
    try:
        if not os.path.exists(model_path):
            print(f"âš ï¸ Ø§Ù†ØªØ¨Ø§Û: '{model_path}' ÙØ§Ø¦Ù„ Ù†ÛÛŒÚº Ù…Ù„ÛŒ")
            return
        
        state_dict = torch.load(model_path, map_location='cpu')
        model.load_state_dict(state_dict)
        print(f"âœ“ ÙˆØ²Ù† Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ù„ÙˆÚˆ ÛÙˆ Ú¯Ø¦Û’: {model_path}")
    except Exception as e:
        print(f"âŒ Ø®Ø±Ø§Ø¨ÛŒ: ÙˆØ²Ù† Ù„ÙˆÚˆ Ú©Ø±ØªÛ’ ÙˆÙ‚Øª Ù…Ø³Ø¦Ù„Û - {str(e)}")
        raise


def export_to_onnx(
    model: PneumoniaModel,
    output_path: str = "backend/app/ml/pneumonia_model.onnx",
    input_shape: Tuple[int, ...] = (1, 3, 224, 224)
) -> None:
    """
    PyTorch Ù…Ø§ÚˆÙ„ Ú©Ùˆ ONNX ÙØ§Ø±Ù…ÛŒÙ¹ Ù…ÛŒÚº Ù…Ø­ÙÙˆØ¸ Ú©Ø±ÛŒÚº
    Ù…ØªØºÛŒØ± Ø¨ÛŒÚ† Ø³Ø§Ø¦Ø² Ú©Û’ Ù„ÛŒÛ’ ÚˆØ§Ø¦Ù†Ø§Ù…Ú© Ø§ÛŒÚ©Ø³ Ú©Û’ Ø³Ø§ØªÚ¾
    
    Parameters:
    -----------
    model : PneumoniaModel
        Ù…Ø§ÚˆÙ„ Ú©ÛŒ Ù…Ø«Ø§Ù„
    output_path : str
        ONNX ÙØ§Ø¦Ù„ Ú©Ùˆ Ù…Ø­ÙÙˆØ¸ Ú©Ø±Ù†Û’ Ú©Ø§ Ø±Ø§Ø³ØªÛ
    input_shape : Tuple[int, ...]
        Ø§Ù† Ù¾Ù¹ Ø´Ú©Ù„ (Ø¨ÛŒÚ† Ø³Ø§Ø¦Ø², Ú†ÛŒÙ†Ù„, Ø§ÙˆÙ†Ú†Ø§Ø¦ÛŒ, Ú†ÙˆÚ‘Ø§Ø¦ÛŒ)
    """
    try:
        print("ðŸ”„ ONNX ÙØ§Ø±Ù…ÛŒÙ¹ Ù…ÛŒÚº Ù…Ø§ÚˆÙ„ Ù…Ù†ØªÙ‚Ù„ Ú©ÛŒØ§ Ø¬Ø§ Ø±ÛØ§ ÛÛ’...")
        
        # Ù…Ø§ÚˆÙ„ Ú©Ùˆ ØªØ¬Ø²ÛŒÛ Ú©Û’ Ù…ÙˆÚˆ Ù…ÛŒÚº Ø±Ú©Ú¾ÛŒÚº
        model.eval()
        
        # Ø¨Ù†Ø§Ø¦ÛŒÚº ÙˆØ§Ù„Ø§ ÚˆÙ…ÛŒ Ø§Ù† Ù¾Ù¹
        dummy_input = torch.randn(*input_shape, dtype=torch.float32)
        
        # ÚˆØ§Ø¦Ù†Ø§Ù…Ú© Ø§ÛŒÚ©Ø³ ØªÛŒØ§Ø± Ú©Ø±ÛŒÚº
        dynamic_axes = {
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
        
        # ÚˆØ§Ø¦Ø±Ú©Ù¹Ø±ÛŒ Ø¨Ù†Ø§Ø¦ÛŒÚº Ø§Ú¯Ø± Ù…ÙˆØ¬ÙˆØ¯ Ù†ÛÛŒÚº ÛÛ’
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # ONNX Ù…ÛŒÚº Ù…Ø§ÚˆÙ„ Ø¨Ø±Ø¢Ù…Ø¯ Ú©Ø±ÛŒÚº
        with torch.no_grad():
            torch.onnx.export(
                model,
                dummy_input,
                output_path,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes=dynamic_axes,
                opset_version=12,
                do_constant_folding=True,
                verbose=False
            )
        
        # ÙØ§Ø¦Ù„ Ú©Ø§ Ø³Ø§Ø¦Ø² Ú†ÛŒÚ© Ú©Ø±ÛŒÚº
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"âœ“ ONNX Ù…Ø§ÚˆÙ„ Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ø¨Ø±Ø¢Ù…Ø¯ ÛÙˆØ§: {output_path}")
        print(f"  ÙØ§Ø¦Ù„ Ø³Ø§Ø¦Ø²: {file_size_mb:.2f} MB")
        
    except Exception as e:
        print(f"âŒ Ø®Ø±Ø§Ø¨ÛŒ: ONNX Ø¨Ø±Ø¢Ù…Ø¯ Ú©Ø±ØªÛ’ ÙˆÙ‚Øª - {str(e)}")
        raise


class PneumoniaONNXPredictor:
    """
    ONNX Ø±Ù† Ù¹Ø§Ø¦Ù… Ø§Ø³ØªØ¹Ù…Ø§Ù„ Ú©Ø±ØªÛ’ ÛÙˆØ¦Û’ Ø§Ù†Ø¯Ø±Ø§Ø² Ù„Ú¯Ø§Ø¦ÛŒÚº
    PNG, JPGØŒ Ø§ÙˆØ± DICOM ÙØ§Ø±Ù…ÛŒÙ¹Ø³ Ú©Ùˆ Ø³Ù¾ÙˆØ±Ù¹ Ú©Ø±ØªØ§ ÛÛ’
    """
    
    # ImageNet Ù†Ø§Ø±Ù…Ù„Ø§Ø¦Ø²ÛŒØ´Ù† Ù¾ÛŒØ±Ø§Ù…ÛŒÙ¹Ø±Ø²
    IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    IMAGE_SIZE = 224
    TEMPERATURE = 1.5  # Ø§Ø¹ØªÙ…Ø§Ø¯ Ú©ÛŒ ØªØ±Ø¯ÙŠØ¯ Ú©Û’ Ù„ÛŒÛ’
    
    # Ø§Ø±Ø¯Ùˆ Ù…ÛŒÚº Ú©Ù„Ø§Ø³ Ú©Û’ Ù„ÛŒØ¨Ù„
    CLASS_LABELS = {
        0: "Ù†Ø§Ø±Ù…Ù„",           # Normal
        1: "Ù†Ù…ÙˆÙ†ÛŒØ§ Ú©Ø§ Ø´Ø¨Û"     # Pneumonia Suspected
    }
    
    def __init__(self, model_path: str = "backend/app/ml/pneumonia_model.onnx"):
        """
        Ø§Ù†Ø¯Ø±Ø§Ø² Ú©Ù†Ù†Ø¯Û Ú©Ùˆ Ø´Ø±ÙˆØ¹ Ú©Ø±ÛŒÚº
        
        Parameters:
        -----------
        model_path : str
            ONNX Ù…Ø§ÚˆÙ„ ÙØ§Ø¦Ù„ Ú©Ø§ Ø±Ø§Ø³ØªÛ
        """
        try:
            print(f"ðŸ“¦ ONNX Ù…Ø§ÚˆÙ„ Ù„ÙˆÚˆ Ú©ÛŒØ§ Ø¬Ø§ Ø±ÛØ§ ÛÛ’: {model_path}")
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Ù…Ø§ÚˆÙ„ ÙØ§Ø¦Ù„ Ù†ÛÛŒÚº Ù…Ù„ÛŒ: {model_path}")
            
            # ONNX Ø±Ù† Ù¹Ø§Ø¦Ù… Ø³ÛŒØ´Ù† Ø´Ø±ÙˆØ¹ Ú©Ø±ÛŒÚº
            self.session = ort.InferenceSession(
                model_path,
                providers=['CPUExecutionProvider']
            )
            
            print("âœ“ ONNX Ø³ÛŒØ´Ù† Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ø´Ø±ÙˆØ¹ ÛÙˆ Ú¯ÛŒØ§")
            
        except Exception as e:
            print(f"âŒ Ø®Ø±Ø§Ø¨ÛŒ: Ù…Ø§ÚˆÙ„ Ù„ÙˆÚˆ Ú©Ø±ØªÛ’ ÙˆÙ‚Øª - {str(e)}")
            raise
    
    def preprocess_image(self, file_path: str) -> np.ndarray:
        """
        ØªØµÙˆÛŒØ± Ú©Ùˆ Ù¾Ø±ÙˆØ³ÛŒØ³ Ú©Ø±ÛŒÚº - PNG, JPGØŒ Ø§ÙˆØ± DICOM ÙØ§Ø±Ù…ÛŒÙ¹Ø³ Ú©Ùˆ Ø³Ù¾ÙˆØ±Ù¹ Ú©Ø±ÛŒÚº
        
        Parameters:
        -----------
        file_path : str
            ØªØµÙˆÛŒØ± ÙØ§Ø¦Ù„ Ú©Ø§ Ø±Ø§Ø³ØªÛ
        
        Returns:
        --------
        np.ndarray
            Ù¾Ø±ÙˆØ³ÛŒØ³ Ø´Ø¯Û ØªØµÙˆÛŒØ± Ù¹ÛŒÙ†Ø³Ø± Ø´Ú©Ù„ (1, 3, 224, 224)
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            
            print(f"ðŸ“· ØªØµÙˆÛŒØ± Ù¾Ø±ÙˆØ³ÛŒØ³ Ú©ÛŒ Ø¬Ø§ Ø±ÛÛŒ ÛÛ’: {file_path}")
            
            # DICOM ÙØ§Ø¦Ù„ Ú©ÛŒ Ø³Ù†Ø¨Ú¾Ø§Ù„ Ú©Ø±ÛŒÚº
            if file_ext == '.dcm':
                if pydicom is None:
                    raise ImportError("DICOM Ø³Ù¾ÙˆØ±Ù¹ Ú©Û’ Ù„ÛŒÛ’ 'pydicom' Ø§Ù†Ø³Ù¹Ø§Ù„ Ú©Ø±ÛŒÚº!")
                
                print("  DICOM ÙØ§Ø±Ù…ÛŒÙ¹ Ø¯Ø±ÛŒØ§ÙØª ÛÙˆØ§")
                dicom_file = pydicom.dcmread(file_path)
                
                # Ù¾Ú©Ø³Ù„ ÚˆÛŒÙ¹Ø§ Ø­Ø§ØµÙ„ Ú©Ø±ÛŒÚº Ø§ÙˆØ± Hounsfield ÛŒÙˆÙ†Ù¹Ø³ Ú©Ùˆ Ù†Ø§Ø±Ù…Ù„ Ú©Ø±ÛŒÚº
                pixel_array = dicom_file.pixel_array.astype(np.float32)
                
                # Hounsfield ÛŒÙˆÙ†Ù¹Ø³ Ú©Ùˆ Ù†Ø§Ø±Ù…Ù„ Ú©Ø±ÛŒÚº (-1024 Ø³Û’ 3071)
                pixel_array = np.clip(pixel_array, -1024, 3071)
                pixel_array = (pixel_array + 1024) / 4095.0
                
                # ØªÛŒÙ† Ú†ÛŒÙ†Ù„Ø² Ù…ÛŒÚº ØªØ¨Ø¯ÛŒÙ„ Ú©Ø±ÛŒÚº
                image = np.stack([pixel_array] * 3, axis=-1)
                
            else:
                # Ù…Ø¹ÛŒØ§Ø±ÛŒ ØªØµÙˆÛŒØ± ÙØ§Ø±Ù…ÛŒÙ¹Ø³ (PNG, JPG)
                print(f"  Ù…Ø¹ÛŒØ§Ø±ÛŒ ØªØµÙˆÛŒØ± ÙØ§Ø±Ù…ÛŒÙ¹: {file_ext}")
                image = Image.open(file_path)
                
                # RGB Ù…ÛŒÚº ØªØ¨Ø¯ÛŒÙ„ Ú©Ø±ÛŒÚº
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # numpy Ù…ÛŒÚº ØªØ¨Ø¯ÛŒÙ„ Ú©Ø±ÛŒÚº
                image = np.array(image, dtype=np.float32)
            
            # 224x224 Ù…ÛŒÚº ØªØ¨Ø¯ÛŒÙ„ Ú©Ø±ÛŒÚº
            if image.shape[:2] != (self.IMAGE_SIZE, self.IMAGE_SIZE):
                pil_image = Image.fromarray(
                    (image * 255).astype(np.uint8) if image.max() <= 1.0 else image.astype(np.uint8)
                )
                pil_image = pil_image.resize(
                    (self.IMAGE_SIZE, self.IMAGE_SIZE),
                    Image.Resampling.LANCZOS
                )
                image = np.array(pil_image, dtype=np.float32)
            
            # 0-1 Ø±ÛŒÙ†Ø¬ Ù…ÛŒÚº Ù†Ø§Ø±Ù…Ù„ Ú©Ø±ÛŒÚº
            if image.max() > 1.0:
                image = image / 255.0
            
            # ImageNet Ù†Ø§Ø±Ù…Ù„Ø§Ø¦Ø²ÛŒØ´Ù† Ù„Ø§Ú¯Ùˆ Ú©Ø±ÛŒÚº
            image = (image - self.IMAGENET_MEAN) / self.IMAGENET_STD
            
            # Ø¨ÛŒÚ† ÚˆØ§Ø¦Ù…Ù†Ø´Ù† Ø´Ø§Ù…Ù„ Ú©Ø±ÛŒÚº: (224, 224, 3) -> (1, 3, 224, 224)
            image = np.transpose(image, (2, 0, 1))
            image = np.expand_dims(image, axis=0)
            
            print(f"âœ“ ØªØµÙˆÛŒØ± Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ù¾Ø±ÙˆØ³ÛŒØ³ ÛÙˆØ¦ÛŒ")
            
            return image.astype(np.float32)
            
        except Exception as e:
            print(f"âŒ Ø®Ø±Ø§Ø¨ÛŒ: ØªØµÙˆÛŒØ± Ù¾Ø±ÙˆØ³ÛŒØ³ Ú©Ø±ØªÛ’ ÙˆÙ‚Øª - {str(e)}")
            raise
    
    def predict(self, image: np.ndarray) -> Dict[str, Union[int, float, str]]:
        """
        ØªØµÙˆÛŒØ± Ú©Û’ Ù„ÛŒÛ’ ØªÙ†Ø¨ÛØ§Øª Ø¯ÛŒÚº
        
        Parameters:
        -----------
        image : np.ndarray
            Ù¾Ø±ÙˆØ³ÛŒØ³ Ø´Ø¯Û ØªØµÙˆÛŒØ± Ø´Ú©Ù„ (1, 3, 224, 224)
        
        Returns:
        --------
        Dict[str, Union[int, float, str]]
            Ù†ØªØ§Ø¦Ø¬ Ú©Ø§ ÚˆÚ©Ø´Ù†Ø±ÛŒ:
            - class_index: 0 (Ù†Ø§Ø±Ù…Ù„) ÛŒØ§ 1 (Ù†Ù…ÙˆÙ†ÛŒØ§)
            - confidence_score: Ø§Ø¹ØªÙ…Ø§Ø¯ Ú©ÛŒ ÙÛŒØµØ¯ (0-100)
            - inference_time_ms: Ø§Ù†Ø¯Ø±Ø§Ø² Ù„Ú¯Ø§Ù†Û’ Ú©Ø§ ÙˆÙ‚Øª Ù…Ù„ÛŒ Ø³ÛŒÚ©Ù†Úˆ Ù…ÛŒÚº
            - status_message: Ø§Ø±Ø¯Ùˆ Ù…ÛŒÚº Ø³Ù¹ÛŒÙ¹Ø³ Ù¾ÛŒØºØ§Ù…
        """
        try:
            # Ø§Ù†Ø¯Ø±Ø§Ø² Ù„Ú¯Ø§Ù†Û’ Ú©Ø§ ÙˆÙ‚Øª Ø´Ø±ÙˆØ¹ Ú©Ø±ÛŒÚº
            start_time = time.time()
            
            print("ðŸ”„ Ù¾ÛŒØ´Ù†Ù†Ú¯ÙˆØ¦ÛŒ Ø¬Ø§Ø±ÛŒ ÛÛ’...")
            
            # ONNX Ø³ÛŒØ´Ù† Ù…ÛŒÚº Ú†Ù„Ø§Ø¦ÛŒÚº
            input_name = self.session.get_inputs()[0].name
            output_name = self.session.get_outputs()[0].name
            
            logits = self.session.run(
                [output_name],
                {input_name: image}
            )[0]
            
            # ÙˆÙ‚Øª Ú©Ø§ Ø­Ø³Ø§Ø¨ Ú©ØªØ§Ø¨ Ú©Ø±ÛŒÚº
            inference_time_ms = int((time.time() - start_time) * 1000)
            
            # Softmax Ù„Ø§Ú¯Ùˆ Ú©Ø±ÛŒÚº Ø¯Ø±Ø¬Û Ø­Ø±Ø§Ø±Øª Ú©Û’ Ø³Ø§ØªÚ¾
            scaled_logits = logits / self.TEMPERATURE
            exp_logits = np.exp(scaled_logits - np.max(scaled_logits, axis=1, keepdims=True))
            confidence_scores = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
            
            # Ø¨ÛØªØ±ÛŒÙ† Ú©Ù„Ø§Ø³ Ú©Ø§ Ø§Ù†ØªØ®Ø§Ø¨ Ú©Ø±ÛŒÚº
            class_index = int(np.argmax(confidence_scores[0]))
            confidence = float(confidence_scores[0][class_index] * 100)
            
            # Ø§Ø±Ø¯Ùˆ Ù…ÛŒÚº Ø³Ù¹ÛŒÙ¹Ø³ Ù¾ÛŒØºØ§Ù…
            status_message = self.CLASS_LABELS.get(class_index, "Ù†Ø§Ù…Ø¹Ù„ÙˆÙ…")
            
            print(f"âœ“ ØªÙ†Ø¨ÛØ§Øª Ù…Ú©Ù…Ù„ ÛÙˆØ¦Û’")
            print(f"  Ù†ØªÛŒØ¬Û: {status_message}")
            print(f"  Ø§Ø¹ØªÙ…Ø§Ø¯: {confidence:.2f}%")
            print(f"  ÙˆÙ‚Øª: {inference_time_ms}ms")
            
            return {
                "class_index": class_index,
                "confidence_score": confidence,
                "inference_time_ms": inference_time_ms,
                "status_message": status_message
            }
            
        except Exception as e:
            print(f"âŒ Ø®Ø±Ø§Ø¨ÛŒ: ØªÙ†Ø¨ÛØ§Øª Ø¯ÛŒØªÛ’ ÙˆÙ‚Øª - {str(e)}")
            raise
    
    def predict_from_file(self, file_path: str) -> Dict[str, Union[int, float, str]]:
        """
        Ø¨Ø±Ø§Û Ø±Ø§Ø³Øª ÙØ§Ø¦Ù„ Ø³Û’ ØªÙ†Ø¨ÛØ§Øª Ø¯ÛŒÚº
        
        Parameters:
        -----------
        file_path : str
            ØªØµÙˆÛŒØ± ÙØ§Ø¦Ù„ Ú©Ø§ Ø±Ø§Ø³ØªÛ (PNGØŒ JPGØŒ ÛŒØ§ DICOM)
        
        Returns:
        --------
        Dict[str, Union[int, float, str]]
            ØªÙ†Ø¨ÛØ§Øª Ú©Û’ Ù†ØªØ§Ø¦Ø¬
        """
        print("\n" + "="*50)
        print("ØªÙ†Ø¨ÛØ§Øª Ú©Û’ Ù„ÛŒÛ’ ØªÛŒØ§Ø±ÛŒ")
        print("="*50)
        
        processed_image = self.preprocess_image(file_path)
        results = self.predict(processed_image)
        
        print("="*50 + "\n")
        
        return results


# Ù¹ÛŒØ³Ù¹ Ø§ÙˆØ± Ù…Ø«Ø§Ù„ Ú©Û’ Ù„ÛŒÛ’ ÙÙ†Ú©Ø´Ù†
def main():
    """
    Ù…Ø§ÚˆÙ„ Ú©Ùˆ Ù¹ÛŒØ³Ù¹ Ú©Ø±ÛŒÚº Ø§ÙˆØ± ONNX Ù…ÛŒÚº Ø¨Ø±Ø¢Ù…Ø¯ Ú©Ø±ÛŒÚº
    """
    print("\n" + "ðŸ¥ Ù¾Ø§Ø¦Ù„Ù…ÙˆÙ†ÛŒØ§ Ú©ÛŒ ØªØ´Ø®ÛŒØµ Ú©Û’ Ù„ÛŒÛ’ ML Ù¾Ø§Ø¦Ù¾ Ù„Ø§Ø¦Ù† Ø´Ø±ÙˆØ¹ ÛÙˆØ¦ÛŒ".center(60))
    print("="*60 + "\n")
    
    try:
        # Ù…Ø§ÚˆÙ„ Ø¨Ù†Ø§Ø¦ÛŒÚº
        model = PneumoniaModel(num_classes=2)
        
        # ONNX Ù…ÛŒÚº Ø¨Ø±Ø¢Ù…Ø¯ Ú©Ø±ÛŒÚº
        export_to_onnx(model, output_path="backend/app/ml/pneumonia_model.onnx")
        
        print("\nâœ“ ML Ù¾Ø§Ø¦Ù¾ Ù„Ø§Ø¦Ù† Ú©Ø§Ù…ÛŒØ§Ø¨ÛŒ Ø³Û’ Ù…Ú©Ù…Ù„ ÛÙˆØ¦ÛŒ!")
        
    except Exception as e:
        print(f"\nâŒ Ø®Ø±Ø§Ø¨ÛŒ: {str(e)}")


if __name__ == "__main__":
    main()
