import io
import logging
from PIL import Image, ImageFilter
import pillow_avif

logger = logging.getLogger(__name__)


def process_image(image_file, width, height, format, quality, strip_metadata=True, smart_sharpen=False, center_crop=False, crop_x=0, crop_y=0, crop_width=None, crop_height=None):
    original_image = None
    
    try:
        original_image = Image.open(image_file)
        original_size = image_file.size
        
        if format == 'JPEG' and original_image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', original_image.size, (255, 255, 255))
            if original_image.mode == 'P':
                original_image = original_image.convert('RGBA')
            background.paste(original_image, mask=original_image.split()[-1] if original_image.mode == 'RGBA' else None)
            original_image.close()
            original_image = background
        
        if crop_width and crop_height:
            original_image = original_image.crop((crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))
        elif center_crop:
            orig_width, orig_height = original_image.size
            target_ratio = width / height
            orig_ratio = orig_width / orig_height
            
            if orig_ratio > target_ratio:
                new_width = int(orig_height * target_ratio)
                left = (orig_width - new_width) // 2
                original_image = original_image.crop((left, 0, left + new_width, orig_height))
            else:
                new_height = int(orig_width / target_ratio)
                top = (orig_height - new_height) // 2
                original_image = original_image.crop((0, top, orig_width, top + new_height))
        
        resized_image = original_image.resize((width, height), Image.Resampling.LANCZOS)
        
        if smart_sharpen:
            resized_image = resized_image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        
        output_buffer = io.BytesIO()
        
        save_kwargs = {}
        if format in ['JPEG', 'WEBP']:
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
        
        if not strip_metadata:
            if 'exif' in original_image.info and format in ['JPEG', 'WEBP']:
                save_kwargs['exif'] = original_image.info['exif']
        
        if format == 'JPEG':
            resized_image.save(output_buffer, format='JPEG', **save_kwargs)
        elif format == 'PNG':
            resized_image.save(output_buffer, format='PNG')
        elif format == 'WEBP':
            resized_image.save(output_buffer, format='WEBP', **save_kwargs)
        elif format == 'AVIF':
            resized_image.save(output_buffer, format='AVIF', quality=quality)
        
        output_buffer.seek(0)
        processed_size = len(output_buffer.getvalue())
        
        resized_image.close()
        
        return output_buffer, original_size, processed_size
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise
    finally:
        if original_image is not None:
            original_image.close()
