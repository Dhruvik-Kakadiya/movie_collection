from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Collection, Movie


class UserSerializer(serializers.ModelSerializer):
    """UserSerializer for registration"""
    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class MovieSerializer(serializers.ModelSerializer):
    """ModelSerializer for movie list"""
    class Meta:
        model = Movie
        fields = ['uuid', 'title', 'description', 'genres']


class CollectionSerializer(serializers.ModelSerializer):
    """ModelSerializer for collection information"""
    movies = MovieSerializer(many=True, write_only=True)

    def validate(self, data):
        # Perform custom validation for movies
        movies_data = data.get('movies', [])
        errors = {}

        for movie_data in movies_data:
            # Create a temporary MovieSerializer for validation
            movie_serializer = MovieSerializer(data=movie_data)
            try:
                movie_serializer.is_valid(raise_exception=True)
            except serializers.ValidationError as e:
                errors.setdefault('movies', []).append({
                    'uuid': movie_data.get('uuid'),
                    'errors': e.detail
                })

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        # Extract movies data from the validated data
        movies_data = validated_data.pop('movies', [])

        # Create the collection instance
        collection = Collection.objects.create(**validated_data)

        # Handle movie creation or retrieval
        for movie_data in movies_data:
            movie, created = Movie.objects.get_or_create(
                uuid=movie_data['uuid'],
                defaults={
                    'title': movie_data.get('title'),
                    'description': movie_data.get('description'),
                    'genres': movie_data.get('genres')
                }
            )
            # Add the movie to the collection
            collection.movies.add(movie)

        return collection

    class Meta:
        model = Collection
        fields = ['title', 'description', 'movies', 'uuid']
        read_only_fields = ['uuid']  # uuid is read-only
