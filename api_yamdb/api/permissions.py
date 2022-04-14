from rest_framework import permissions


class IsAdminModeratorOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение доступа только для чтения или только для администратора,
    модератора и автора.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moderator
            or obj.author == request.user
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение доступа только для чтения или только для администратора.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )


class AdminOnly(permissions.BasePermission):
    """
    Разрешение на редактирование только для администратора.
    """
    def has_permission(self, request, view):
        return request.user.is_admin or request.user.is_staff
