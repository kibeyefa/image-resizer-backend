import logging
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.http import HttpResponse

from .serializers import ImageProcessSerializer
from .utils import process_image

logger = logging.getLogger(__name__)


class ImageResizeView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        request=ImageProcessSerializer,
        responses={
            200: {
                'type': 'string',
                'format': 'binary',
                'description': 'Resized image file'
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        description='Resize an image with specified dimensions, format, and quality.',
        examples=[
            OpenApiExample(
                'Resize image example',
                value={
                    'file': '(binary)',
                    'width': 1920,
                    'height': 1080,
                    'format': 'WEBP',
                    'quality': 85
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        start_time = time.time()
        
        serializer = ImageProcessSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.warning(f"Validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        image_file = validated_data['file']
        width = validated_data['width']
        height = validated_data['height']
        format = validated_data.get('format', 'JPEG')
        quality = validated_data.get('quality', 80)
        strip_metadata = validated_data.get('strip_metadata', True)
        smart_sharpen = validated_data.get('smart_sharpen', False)
        center_crop = validated_data.get('center_crop', False)
        crop_x = validated_data.get('crop_x', 0)
        crop_y = validated_data.get('crop_y', 0)
        crop_width = validated_data.get('crop_width')
        crop_height = validated_data.get('crop_height')
        
        try:
            logger.info(f"Processing image: {image_file.name}, {width}x{height}, {format}, quality={quality}")
            
            output_buffer, original_size, processed_size = process_image(
                image_file, width, height, format, quality,
                strip_metadata=strip_metadata,
                smart_sharpen=smart_sharpen,
                center_crop=center_crop,
                crop_x=crop_x,
                crop_y=crop_y,
                crop_width=crop_width,
                crop_height=crop_height
            )
            
            content_type_map = {
                'JPEG': 'image/jpeg',
                'PNG': 'image/png',
                'WEBP': 'image/webp',
                'AVIF': 'image/avif'
            }
            
            processing_time = time.time() - start_time
            logger.info(
                f"Image processed successfully: original={original_size}B, "
                f"processed={processed_size}B, time={processing_time:.2f}s"
            )
            
            response = HttpResponse(
                output_buffer.getvalue(),
                content_type=content_type_map.get(format, 'image/jpeg')
            )
            response['X-Original-Size'] = str(original_size)
            response['X-Processed-Size'] = str(processed_size)
            response['X-Processing-Time'] = f"{processing_time:.2f}s"
            response['Content-Disposition'] = f'attachment; filename="resized_image.{format.lower()}"'
            
            output_buffer.close()
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to process image: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to process image. Please ensure the file is a valid image.'},
                status=status.HTTP_400_BAD_REQUEST
            )
