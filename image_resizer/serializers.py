import logging
from rest_framework import serializers

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/avif', 'image/gif']


class ImageProcessSerializer(serializers.Serializer):
    file = serializers.ImageField(help_text="Image file to resize")
    width = serializers.IntegerField(help_text="Target width in pixels", min_value=1, max_value=10000)
    height = serializers.IntegerField(help_text="Target height in pixels", min_value=1, max_value=10000)
    
    format = serializers.CharField(
        max_length=10,
        default='JPEG',
        help_text="Output format for the resized image. Options: JPEG, PNG, WEBP, AVIF"
    )
    
    quality = serializers.IntegerField(
        min_value=1,
        max_value=100,
        default=80,
        help_text="Quality factor for compression (1-100)"
    )
    
    strip_metadata = serializers.BooleanField(
        default=True,
        help_text="Strip EXIF and other metadata from the image"
    )
    
    smart_sharpen = serializers.BooleanField(
        default=False,
        help_text="Apply smart sharpening to the image"
    )
    
    center_crop = serializers.BooleanField(
        default=False,
        help_text="Center crop the image to exact dimensions instead of resizing"
    )
    
    crop_x = serializers.IntegerField(
        required=False,
        default=0,
        help_text="X offset for custom crop"
    )
    
    crop_y = serializers.IntegerField(
        required=False,
        default=0,
        help_text="Y offset for custom crop"
    )
    
    crop_width = serializers.IntegerField(
        required=False,
        allow_null=True,
        default=None,
        help_text="Width of custom crop region"
    )
    
    crop_height = serializers.IntegerField(
        required=False,
        allow_null=True,
        default=None,
        help_text="Height of custom crop region"
    )

    def validate_file(self, value):
        if value.size > MAX_FILE_SIZE:
            logger.warning(f"File size exceeded: {value.size} bytes")
            raise serializers.ValidationError(f'File size exceeds the {MAX_FILE_SIZE // (1024*1024)}MB limit.')
        
        if value.content_type not in ALLOWED_TYPES:
            logger.warning(f"Invalid file type: {value.content_type}")
            raise serializers.ValidationError(
                f'File type not supported. Allowed types: JPEG, PNG, WEBP, AVIF, GIF'
            )
        
        return value

    def validate_format(self, value):
        allowed_formats = ['JPEG', 'PNG', 'WEBP', 'AVIF']
        if value.upper() not in allowed_formats:
            raise serializers.ValidationError(f"Format must be one of {allowed_formats}")
        return value.upper()
