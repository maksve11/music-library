from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenreViewSet, ArtistViewSet, AlbumViewSet, TrackViewSet, UserProfileViewSet, RecommendationViewSet

router = DefaultRouter()
router.register(r'genres', GenreViewSet)
router.register(r'artists', ArtistViewSet)
router.register(r'albums', AlbumViewSet)
router.register(r'tracks', TrackViewSet)
router.register(r'user_profiles', UserProfileViewSet, basename='userprofile')
router.register(r'recommendations', RecommendationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
