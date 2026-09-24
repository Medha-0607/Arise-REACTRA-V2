"""REACTRA V2 — Scientific Image I/O & Provenance Ingestion.

Validates raw image data, channels, dimensions, format, and explicit provenance.
Section References: PRD V2 §10, Master Build Spec §10.
"""

import base64
import hashlib
import io
from typing import Optional, Tuple, Union
import cv2
import numpy as np
from PIL import Image


class ImageValidationError(ValueError):
    """Raised when an input image fails basic validation."""
    pass


class IngestedImage:
    """Validated in-memory image container."""
    def __init__(
        self,
        rgb_array: np.ndarray,
        provenance: str,
        sha256_hash: str,
        width: int,
        height: int,
        channels: int,
        source_format: str,
    ):
        self.rgb_array = rgb_array
        self.provenance = provenance
        self.sha256_hash = sha256_hash
        self.width = width
        self.height = height
        self.channels = channels
        self.source_format = source_format

    def to_bgr(self) -> np.ndarray:
        """Convert RGB to OpenCV BGR format."""
        return cv2.cvtColor(self.rgb_array, cv2.COLOR_RGB2BGR)

    def to_grayscale(self) -> np.ndarray:
        """Convert RGB to 8-bit grayscale."""
        return cv2.cvtColor(self.rgb_array, cv2.COLOR_RGB2GRAY)


def ingest_image_data(
    image_source: Union[bytes, str],
    provenance: str = "LIVE_CAMERA",
    min_width: int = 320,
    min_height: int = 240,
    max_dimension: int = 4096,
) -> IngestedImage:
    """Ingest, validate, and decode an image from bytes, base64 string, or filepath.
    
    Parameters
    ----------
    image_source : bytes or str
        Raw image bytes, base64 data string, or filesystem path.
    provenance : str
        Explicit capture mode ('LIVE_CAMERA' or 'IMPORTED_IMAGE').
    min_width, min_height : int
        Minimum spatial dimensions.
    max_dimension : int
        Maximum allowed width/height.
        
    Returns
    -------
    IngestedImage
        Validated container with standard RGB uint8 numpy array.
    """
    # 1. Provenance validation
    norm_provenance = provenance.upper().strip()
    if norm_provenance not in ("LIVE_CAMERA", "DIRECT_CAMERA", "IMPORTED_IMAGE"):
        raise ImageValidationError(
            f"Invalid provenance '{provenance}'. Must be 'LIVE_CAMERA' or 'IMPORTED_IMAGE'."
        )
    # Standardize to LIVE_CAMERA or IMPORTED_IMAGE
    if norm_provenance in ("DIRECT_CAMERA", "LIVE_CAMERA"):
        norm_provenance = "LIVE_CAMERA"

    # 2. Extract raw bytes
    raw_bytes: bytes
    if isinstance(image_source, bytes):
        raw_bytes = image_source
    elif isinstance(image_source, str):
        if image_source.startswith("data:image"):
            # Base64 data URL
            try:
                base64_data = image_source.split(",", 1)[1]
                raw_bytes = base64.b64decode(base64_data)
            except Exception as e:
                raise ImageValidationError(f"Malformed base64 image data URL: {e}")
        elif len(image_source) > 500 and not image_source.endswith((".png", ".jpg", ".jpeg")):
            # Raw base64 string
            try:
                raw_bytes = base64.b64decode(image_source)
            except Exception as e:
                raise ImageValidationError(f"Malformed base64 string: {e}")
        else:
            # File path
            try:
                with open(image_source, "rb") as f:
                    raw_bytes = f.read()
            except Exception as e:
                raise ImageValidationError(f"Failed to read image file '{image_source}': {e}")
    else:
        raise ImageValidationError(f"Unsupported image source type: {type(image_source)}")

    if not raw_bytes or len(raw_bytes) < 64:
        raise ImageValidationError("Empty or corrupted image payload.")

    # 3. Calculate SHA-256 digest
    sha256_hash = hashlib.sha256(raw_bytes).hexdigest()

    # 4. Decode image format via PIL & OpenCV
    try:
        pil_img = Image.open(io.BytesIO(raw_bytes))
        source_format = pil_img.format or "UNKNOWN"
        # Convert PIL to standard RGB
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        rgb_array = np.array(pil_img, dtype=np.uint8)
    except Exception as e:
        raise ImageValidationError(f"Failed to decode image buffer: {e}")

    height, width = rgb_array.shape[:2]
    channels = rgb_array.shape[2] if rgb_array.ndim == 3 else 1

    # 5. Validate dimensions & channels
    if channels != 3:
        raise ImageValidationError(f"Image must have exactly 3 color channels (RGB), found {channels}.")

    if width < min_width or height < min_height:
        raise ImageValidationError(
            f"Image dimensions ({width}x{height}) are below required minimum ({min_width}x{min_height})."
        )

    if width > max_dimension or height > max_dimension:
        raise ImageValidationError(
            f"Image dimensions ({width}x{height}) exceed maximum allowed dimension ({max_dimension})."
        )

    return IngestedImage(
        rgb_array=rgb_array,
        provenance=norm_provenance,
        sha256_hash=sha256_hash,
        width=width,
        height=height,
        channels=channels,
        source_format=source_format,
    )
