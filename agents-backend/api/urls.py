from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    RoleViewSet,
    PermissionViewSet,
    ModelConfigViewSet,
    ChatView,
    me,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"roles", RoleViewSet)
router.register(r"permissions", PermissionViewSet)
router.register(r"model-configs", ModelConfigViewSet)

urlpatterns = [
    path("auth/me/", me, name="me"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("chat/", ChatView.as_view(), name="chat"),
    path("", include(router.urls)),
]
