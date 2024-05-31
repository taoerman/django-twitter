from rest_framework.permissions import BasePermission

class IsObjectOwner(BasePermission):

    """
    this permission is charge of checking obj.user == request.user?
    this class can be used by other classes, we can put this permission
    class into a sharing class.
    if detail = False, only check the has_permission
    if detail = True, both two function would be used to check
    if wrong, the default info will show IsObjectOwner.message
    """
    message = "You do not have permission to access this object"
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        """
        in api/views, we write querySet = Comment.objects.all()
        api could execute self.getObjects() automatically to get current obj
        """
        return request.user == obj.user