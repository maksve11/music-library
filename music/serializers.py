from rest_framework import serializers
from .models import Genre, Artist, Album, Track, UserProfile, Recommendation


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    favorite_genres = GenreSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = '__all__'


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'


class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer()

    class Meta:
        model = Album
        fields = '__all__'


class TrackSerializer(serializers.ModelSerializer):
    album = AlbumSerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        model = Track
        fields = '__all__'


class RecommendationSerializer(serializers.ModelSerializer):
    track = TrackSerializer()

    class Meta:
        model = Recommendation
        fields = '__all__'