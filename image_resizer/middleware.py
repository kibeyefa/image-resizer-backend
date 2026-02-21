import time
from django.core.cache import cache
from django.http import JsonResponse


class RateLimitMiddleware:
    RATE_LIMIT = 100
    RATE_PERIOD = 3600

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/api/v1/health/':
            return self.get_response(request)

        ip = self.get_client_ip(request)
        cache_key = f'ratelimit_{ip}'

        requests = cache.get(cache_key, 0)

        if requests >= self.RATE_LIMIT:
            return JsonResponse(
                {'error': 'Rate limit exceeded. Please try again later.'},
                status=429
            )

        if requests == 0:
            cache.set(cache_key, 1, self.RATE_PERIOD)
        else:
            cache.incr(cache_key)

        response = self.get_response(request)
        response['X-RateLimit-Limit'] = str(self.RATE_LIMIT)
        response['X-RateLimit-Remaining'] = str(max(0, self.RATE_LIMIT - requests - 1))
        response['X-RateLimit-Reset'] = str(cache.ttl(cache_key) if hasattr(cache, 'ttl') else self.RATE_PERIOD)

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '127.0.0.1')
