from rest_framework.response import Response
from rest_framework import status
from functools import wraps

def required_params(request_attr='query_params', params=None):
    """
    当我们使用@required_params(params=['some_param'])的时候
    这个required_params函数应该需要返回一个 decorator 函数，这个 decorator
    函数的参数就是被@required_params包裹起来的函数view_func
    """
    if params is None:
        return []

    def decorator(view_func):

        @wraps(view_func)
        def _wrapped_view(instance, request, *args, **kwargs):
            data = getattr(request, request_attr)
            missing_params = [
                param
                for param in params
                if param not in data
            ]
            if missing_params:
                params_str = ','.join(missing_params)
                return Response({
                    'message' : u'missing{} in request'.format(params_str),
                    'success' : False,
                }, status=status.HTTP_400_BAD_REQUEST)
            return view_func(instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator