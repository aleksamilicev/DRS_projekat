from .adminRoutes.adminRoutes import admin_routes
from .notificationRoutes.notificationRoutes import notification_routes
from .postsRoutes.postsRoutes import post_routes
from .userProfileRoutes.userProfileRoutes import user_profile_routes
from .authRoutes.authRoutes import auth_routes
from .friendsRoutes.friendsRoutes import friends_routes
from .searchRoutes.searchRoutes import search_routes

__all__ = [
    "admin_routes",
    "notification_routes",
    "post_routes",
    "user_profile_routes",
    "auth_routes",
    "friends_routes",
    "search_routes"
]
