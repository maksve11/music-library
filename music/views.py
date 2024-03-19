from django.contrib.auth.models import User
from requests import Response
from rest_framework import viewsets, generics

from .models import Genre, Artist, Album, Track, UserProfile, Recommendation
from .serializers import GenreSerializer, ArtistSerializer, AlbumSerializer, TrackSerializer, UserProfileSerializer, \
    RecommendationSerializer
import tensorflow as tf
import tensorflow_recommenders as tfrs


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserProfileListCreateView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserProfileRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class RecommendationListCreateView(generics.ListCreateAPIView):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer


class RecommendationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer


class TrackViewSet(viewsets.ModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer


class RecommendationViewSet(viewsets.ViewSet):
    queryset = Recommendation.objects.all()

    def list(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'})

        user = User.objects.get(pk=user_id)
        profile = user.userprofile

        # Получить все треки, которые пользователь еще не слушал
        listened_tracks = Recommendation.objects.filter(user=user).values_list('track_id', flat=True)
        unlistened_tracks = Track.objects.exclude(pk__in=listened_tracks)

        # Получить жанры, которые пользователь выбрал в качестве любимых
        favorite_genres = profile.favorite_genres.all()

        # Получить все треки из любимых жанров пользователя
        favorite_tracks = Track.objects.filter(genre__in=favorite_genres)

        # Подготовить данные для модели
        ratings = tf.data.Dataset.from_generator(
            lambda: Recommendation.objects.all().iterator(),
            output_types=(tf.int64, tf.int64, tf.float32),
            output_shapes=((), (), ())
        )
        users = ratings.map(lambda x, _, __: x)
        items = ratings.map(lambda _, x, __: x)
        ratings_dataset = ratings.batch(100)

        # Создать модель рекомендаций
        model = tfrs.models.FactorizedTopN(
            user_model=tfrs.models.UserModel(users),
            item_model=tfrs.models.ItemModel(items),
            user_item_model=tfrs.models.FactorizedItemModel(items)
        )

        # Обучить модель и получить рекомендации
        model.compile(optimizer=tf.keras.optimizers.Adagrad(learning_rate=0.1))
        model.fit(ratings_dataset, epochs=5)
        recommendations = []
        for track in unlistened_tracks:
            scores = model.predict(tf.constant([int(user_id)]), tf.constant([track.id]))
            recommendations.append((track, scores[0, 0]))
        recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)

        # Добавить в рекомендации треки из любимых жанров пользователя
        for track in favorite_tracks:
            if track not in [r[0] for r in recommendations]:
                recommendations.append((track, 0))
        recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)

        # Вернуть рекомендации
        recommendations = [TrackSerializer(r[0]).data for r in recommendations[:10]]
        return Response(recommendations)
