"""
CloudFace Pro - Watermark Processor
Handles watermarking of photos for professional photographers
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import Optional, Tuple
import os


class WatermarkProcessor:
    """Process watermarks for photos"""
    
    def __init__(self):
        self.default_font_size = 24
        self.margin = 20
    
    def add_watermark_to_image(self, image_bytes: bytes, event_data: dict) -> bytes:
        """
        Add watermark to image based on event settings
        
        Args:
            image_bytes: Original image bytes
            event_data: Event configuration with watermark settings
            
        Returns:
            Watermarked image bytes
        """
        if not event_data.get('enable_watermark', False):
            return image_bytes
        
        try:
            # Load image
            image = Image.open(BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            watermark_type = event_data.get('watermark_type', 'text')
            
            if watermark_type == 'text':
                watermarked = self._add_text_watermark(image, event_data)
            elif watermark_type == 'logo':
                watermarked = self._add_logo_watermark(image, event_data)
            else:
                return image_bytes
            
            # Convert back to bytes
            output = BytesIO()
            watermarked.save(output, format='JPEG', quality=95)
            return output.getvalue()
            
        except Exception as e:
            print(f"⚠️ Watermark error: {e}")
            return image_bytes  # Return original if watermarking fails
    
    def _add_text_watermark(self, image: Image.Image, event_data: dict) -> Image.Image:
        """Add text watermark to image"""
        watermark_text = event_data.get('watermark_text', '')
        if not watermark_text:
            return image
        
        # Create a copy to work with
        watermarked = image.copy()
        
        # Get image dimensions
        width, height = watermarked.size
        
        # Create transparent overlay
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Try to load a font, fallback to default
        try:
            font_size = max(16, min(width, height) // 30)  # Scale with image size
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate position
        position = self._calculate_position(
            event_data.get('watermark_position', 'bottom_left'),
            width, height, text_width, text_height
        )
        
        # Get opacity
        opacity = event_data.get('watermark_opacity', 70)
        alpha = int(255 * opacity / 100)
        
        # Draw text with semi-transparent background
        padding = 8
        bg_rect = [
            position[0] - padding,
            position[1] - padding,
            position[0] + text_width + padding,
            position[1] + text_height + padding
        ]
        
        # Semi-transparent background
        draw.rectangle(bg_rect, fill=(0, 0, 0, alpha // 2))
        
        # White text
        draw.text(position, watermark_text, font=font, fill=(255, 255, 255, alpha))
        
        # Composite overlay onto image
        watermarked = Image.alpha_composite(
            watermarked.convert('RGBA'), overlay
        ).convert('RGB')
        
        return watermarked
    
    def _add_logo_watermark(self, image: Image.Image, event_data: dict) -> Image.Image:
        """Add logo watermark to image"""
        from cloudface_pro_storage import storage
        
        event_id = event_data.get('event_id')
        logo_filename = event_data.get('watermark_logo_filename')
        
        if not event_id or not logo_filename:
            return image
        
        # Load logo
        logo_bytes = storage.get_event_watermark_logo(event_id, logo_filename)
        if not logo_bytes:
            print(f"⚠️ Watermark logo not found: {logo_filename}")
            return image
        
        try:
            logo = Image.open(BytesIO(logo_bytes))
            
            # Convert logo to RGBA if needed
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')
            
            # Get image dimensions
            img_width, img_height = image.size
            logo_width, logo_height = logo.size
            
            # Scale logo to fit (max 20% of image width)
            max_logo_width = int(img_width * 0.2)
            if logo_width > max_logo_width:
                scale = max_logo_width / logo_width
                new_width = int(logo_width * scale)
                new_height = int(logo_height * scale)
                logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logo_width, logo_height = new_width, new_height
            
            # Calculate position
            position = self._calculate_position(
                event_data.get('watermark_position', 'bottom_left'),
                img_width, img_height, logo_width, logo_height
            )
            
            # Apply opacity
            opacity = event_data.get('watermark_opacity', 70)
            alpha = int(255 * opacity / 100)
            
            # Create logo with adjusted opacity
            logo_with_alpha = Image.new('RGBA', logo.size, (0, 0, 0, 0))
            for x in range(logo.width):
                for y in range(logo.height):
                    pixel = logo.getpixel((x, y))
                    if len(pixel) == 4 and pixel[3] > 0:  # Has alpha
                        logo_with_alpha.putpixel((x, y), (pixel[0], pixel[1], pixel[2], alpha))
            
            # Create transparent overlay
            overlay = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
            overlay.paste(logo_with_alpha, position)
            
            # Composite onto image
            watermarked = Image.alpha_composite(
                image.convert('RGBA'), overlay
            ).convert('RGB')
            
            return watermarked
            
        except Exception as e:
            print(f"⚠️ Logo watermark error: {e}")
            return image
    
    def _calculate_position(self, position: str, img_width: int, img_height: int, 
                          watermark_width: int, watermark_height: int) -> Tuple[int, int]:
        """Calculate watermark position with margin"""
        
        if position == 'top_left':
            x = self.margin
            y = self.margin
        elif position == 'top_right':
            x = img_width - watermark_width - self.margin
            y = self.margin
        elif position == 'bottom_right':
            x = img_width - watermark_width - self.margin
            y = img_height - watermark_height - self.margin
        else:  # bottom_left (default)
            x = self.margin
            y = img_height - watermark_height - self.margin
        
        return (x, y)


# Global instance
watermark_processor = WatermarkProcessor()
