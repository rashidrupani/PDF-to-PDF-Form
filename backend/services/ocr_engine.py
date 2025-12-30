"""
OCR Engine Service for Document Processing
Handles multi-engine OCR processing with confidence scoring and field detection
"""
import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
import easyocr
import paddleocr
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

@dataclass
class OCRResult:
    """Represents OCR result for a text region"""
    text: str
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float
    engine: str  # 'tesseract', 'easyocr', 'paddleocr'

@dataclass
class Field:
    """Represents a detected form field"""
    name: str
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    field_type: str  # 'text', 'checkbox', 'radio', 'signature', 'dropdown'
    value: str = ""
    confidence: float = 0.0

@dataclass
class ExtractionResult:
    """Complete extraction result from OCR pipeline"""
    text_blocks: List[OCRResult]
    fields: List[Field]
    confidence_scores: Dict[str, float]
    processing_time: float

class OCRType(Enum):
    TESSERACT = "tesseract"
    EASYOCR = "easyocr"
    PADDLEOCR = "paddleocr"

class TesseractEngine:
    """Tesseract OCR engine wrapper"""

    def __init__(self):
        # Configure tesseract with common configurations
        self.config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz -c preserve_interword_spaces=1'

    def process_image(self, image: np.ndarray) -> List[OCRResult]:
        """
        Process image with Tesseract OCR
        Returns list of OCRResult objects
        """
        try:
            # Get detailed data from tesseract
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=self.config)

            results = []
            n_boxes = len(data['level'])

            for i in range(n_boxes):
                if int(data['conf'][i]) > 0:  # Only include if confidence > 0
                    text = data['text'][i].strip()
                    if text:  # Only include non-empty text
                        x = data['left'][i]
                        y = data['top'][i]
                        w = data['width'][i]
                        h = data['height'][i]

                        results.append(OCRResult(
                            text=text,
                            bbox=(x, y, w, h),
                            confidence=float(data['conf'][i]) / 100.0,  # Convert to 0-1 scale
                            engine=OCRType.TESSERACT.value
                        ))

            return results
        except Exception as e:
            logger.error(f"Tesseract processing error: {str(e)}")
            return []

class EasyOCREngine:
    """EasyOCR engine wrapper"""

    def __init__(self, languages=['en']):
        self.reader = easyocr.Reader(languages, gpu=False)

    def process_image(self, image: np.ndarray) -> List[OCRResult]:
        """
        Process image with EasyOCR
        Returns list of OCRResult objects
        """
        try:
            # EasyOCR expects RGB format
            if len(image.shape) == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

            # Perform OCR
            results = self.reader.readtext(rgb_image, detail=1, paragraph=False)

            ocr_results = []
            for (bbox, text, confidence) in results:
                # Convert bbox format from [[x1,y1], [x2,y2], [x3,y3], [x4,y4]] to (x, y, w, h)
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]

                x = min(x_coords)
                y = min(y_coords)
                w = max(x_coords) - x
                h = max(y_coords) - y

                ocr_results.append(OCRResult(
                    text=text,
                    bbox=(int(x), int(y), int(w), int(h)),
                    confidence=min(confidence, 1.0),  # Ensure confidence is <= 1.0
                    engine=OCRType.EASYOCR.value
                ))

            return ocr_results
        except Exception as e:
            logger.error(f"EasyOCR processing error: {str(e)}")
            return []

class PaddleOCREngine:
    """PaddleOCR engine wrapper"""

    def __init__(self):
        # Initialize PaddleOCR with CPU (GPU can be enabled if needed)
        self.ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)

    def process_image(self, image: np.ndarray) -> List[OCRResult]:
        """
        Process image with PaddleOCR
        Returns list of OCRResult objects
        """
        try:
            # PaddleOCR expects RGB format
            if len(image.shape) == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

            # Perform OCR
            result = self.ocr.ocr(rgb_image, cls=True)

            ocr_results = []
            if result and result[0]:  # Check if result exists and has data
                for detection in result[0]:
                    bbox = detection[0]  # Coordinates [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    text = detection[1][0]  # Text
                    confidence = detection[1][1]  # Confidence score

                    # Convert bbox format to (x, y, w, h)
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]

                    x = min(x_coords)
                    y = min(y_coords)
                    w = max(x_coords) - x
                    h = max(y_coords) - y

                    ocr_results.append(OCRResult(
                        text=text,
                        bbox=(int(x), int(y), int(w), int(h)),
                        confidence=min(confidence, 1.0),  # Ensure confidence is <= 1.0
                        engine=OCRType.PADDLEOCR.value
                    ))

            return ocr_results
        except Exception as e:
            logger.error(f"PaddleOCR processing error: {str(e)}")
            return []

class OCREngine:
    """Main OCR Engine that orchestrates multiple OCR engines"""

    def __init__(self):
        self.tesseract_engine = TesseractEngine()
        self.easyocr_engine = EasyOCREngine()
        self.paddleocr_engine = PaddleOCREngine()

    def process_document(self, document_path: str) -> ExtractionResult:
        """
        Process entire document through OCR pipeline
        Returns structured extraction result
        """
        import time
        start_time = time.time()

        # Load and preprocess document
        pages = self._load_document(document_path)

        all_text_blocks = []
        all_fields = []

        for page_idx, page_image in enumerate(pages):
            # Preprocess the page
            preprocessed_page = self._preprocess_image(page_image)

            # Run all OCR engines on the page
            tesseract_results = self.tesseract_engine.process_image(preprocessed_page)
            easyocr_results = self.easyocr_engine.process_image(preprocessed_page)
            paddleocr_results = self.paddleocr_engine.process_image(preprocessed_page)

            # Combine results from all engines
            combined_results = self._combine_ocr_results(
                tesseract_results, easyocr_results, paddleocr_results
            )

            all_text_blocks.extend(combined_results)

        # Detect form fields
        fields = self._detect_form_fields(all_text_blocks)

        # Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(all_text_blocks, fields)

        processing_time = time.time() - start_time

        return ExtractionResult(
            text_blocks=all_text_blocks,
            fields=fields,
            confidence_scores=confidence_scores,
            processing_time=processing_time
        )

    def _load_document(self, document_path: str) -> List[np.ndarray]:
        """
        Load document and convert to list of images (pages)
        Handles PDF, JPG, PNG, TIFF formats
        """
        import fitz  # PyMuPDF
        import io

        extension = os.path.splitext(document_path)[1].lower()

        if extension == '.pdf':
            # Handle PDF files
            doc = fitz.open(document_path)
            pages = []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better resolution
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                img_array = np.array(img)
                pages.append(img_array)

            doc.close()
            return pages

        else:
            # Handle image files (JPG, PNG, TIFF)
            img = cv2.imread(document_path)
            if img is None:
                raise ValueError(f"Could not load image: {document_path}")
            return [img]

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results
        Includes denoising, contrast adjustment, binarization
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        # Apply adaptive threshold for binarization
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(binary)

        return enhanced

    def _combine_ocr_results(self, tesseract_results: List[OCRResult],
                           easyocr_results: List[OCRResult],
                           paddleocr_results: List[OCRResult]) -> List[OCRResult]:
        """
        Combine results from multiple OCR engines using ensemble voting
        """
        # Group results by spatial proximity
        all_results = tesseract_results + easyocr_results + paddleocr_results

        # Simple grouping algorithm - group results that overlap significantly
        grouped_results = []
        processed = set()

        for i, result in enumerate(all_results):
            if i in processed:
                continue

            # Find overlapping results
            overlapping = [result]
            processed.add(i)

            for j, other_result in enumerate(all_results[i+1:], i+1):
                if j in processed:
                    continue

                if self._boxes_overlap(result.bbox, other_result.bbox):
                    overlapping.append(other_result)
                    processed.add(j)

            # Create combined result
            if len(overlapping) == 1:
                grouped_results.append(overlapping[0])
            else:
                # Take the result with highest confidence, or average if tied
                best_result = max(overlapping, key=lambda r: r.confidence)
                grouped_results.append(best_result)

        return grouped_results

    def _boxes_overlap(self, box1: Tuple[int, int, int, int],
                      box2: Tuple[int, int, int, int],
                      threshold: float = 0.5) -> bool:
        """
        Check if two bounding boxes overlap significantly
        """
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2

        # Calculate intersection
        left = max(x1, x2)
        top = max(y1, y2)
        right = min(x1 + w1, x2 + w2)
        bottom = min(y1 + h1, y2 + h2)

        if left < right and top < bottom:
            intersection_area = (right - left) * (bottom - top)
            box1_area = w1 * h1
            box2_area = w2 * h2
            union_area = box1_area + box2_area - intersection_area

            if union_area > 0:
                overlap_ratio = intersection_area / union_area
                return overlap_ratio >= threshold

        return False

    def _detect_form_fields(self, text_blocks: List[OCRResult]) -> List[Field]:
        """
        Detect form fields based on text patterns and positions
        """
        fields = []

        for block in text_blocks:
            # Simple heuristic-based field detection
            text_lower = block.text.lower().strip()

            # Look for common field indicators
            if any(keyword in text_lower for keyword in ['name', 'first name', 'last name', 'surname']):
                fields.append(Field(
                    name='name',
                    bbox=block.bbox,
                    field_type='text',
                    value='',
                    confidence=block.confidence
                ))
            elif any(keyword in text_lower for keyword in ['email', 'e-mail', 'mail']):
                fields.append(Field(
                    name='email',
                    bbox=block.bbox,
                    field_type='text',
                    value='',
                    confidence=block.confidence
                ))
            elif any(keyword in text_lower for keyword in ['phone', 'tel', 'mobile', 'cell']):
                fields.append(Field(
                    name='phone',
                    bbox=block.bbox,
                    field_type='text',
                    value='',
                    confidence=block.confidence
                ))
            elif any(keyword in text_lower for keyword in ['date', 'dob', 'birth']):
                fields.append(Field(
                    name='date',
                    bbox=block.bbox,
                    field_type='text',
                    value='',
                    confidence=block.confidence
                ))
            elif any(keyword in text_lower for keyword in ['address', 'street', 'city', 'state', 'zip', 'postal']):
                fields.append(Field(
                    name='address',
                    bbox=block.bbox,
                    field_type='text',
                    value='',
                    confidence=block.confidence
                ))
            elif any(keyword in text_lower for keyword in ['account', 'iban', 'number']):
                fields.append(Field(
                    name='account_number',
                    bbox=block.bbox,
                    field_type='text',
                    value='',
                    confidence=block.confidence
                ))
            # Add more field detection rules as needed

        return fields

    def _calculate_confidence_scores(self, text_blocks: List[OCRResult],
                                   fields: List[Field]) -> Dict[str, float]:
        """
        Calculate overall confidence scores for the document
        """
        if not text_blocks:
            return {'overall': 0.0, 'average_per_block': 0.0, 'min': 0.0, 'max': 0.0}

        confidences = [block.confidence for block in text_blocks]

        return {
            'overall': sum(confidences) / len(confidences) if confidences else 0.0,
            'average_per_block': sum(confidences) / len(confidences) if confidences else 0.0,
            'min': min(confidences) if confidences else 0.0,
            'max': max(confidences) if confidences else 0.0,
            'total_blocks': len(text_blocks)
        }