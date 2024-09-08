from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Collection, Movie, RequestCount
from movies.serializer import UserSerializer, CollectionSerializer
import requests
from movie_collection import settings
from django.db import transaction

from .utils import compute_favorite_genres
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class RegisterUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """API to register user"""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {"access_token": str(refresh.access_token)},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MovieListView(APIView):
    def get(self, request):
        """API to fetch list of movies with retry mechanism"""

        # Create a retry strategy
        retry_strategy = Retry(
            total=3,  # Total number of retries
            backoff_factor=1,  # Wait time between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
        )

        # Create an HTTPAdapter with the retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)

        # Create a session and mount the adapter
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)

        try:
            # Make the GET request to the third-party API
            response = http.get(
                settings.MOVIE_LIST_URL,
                auth=(settings.MOVIE_API_USERNAME, settings.MOVIE_API_PASSWORD),
                verify=False,  # Disable SSL verification
                timeout=10  # Set a timeout for the request
            )

            # Check if the response is not successful
            if response.status_code != 200:
                return Response(
                    {"error": "Failed to fetch movies"},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            # Return the response data
            return Response(response.json(), status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            # Handle any request exceptions
            return Response(
                {"error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )


class CollectionListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """API to fetch list of collections"""

        # Get all collections for the authenticated user
        collections = Collection.objects.filter(user=request.user)
        serializer = CollectionSerializer(collections, many=True)

        # Compute favorite genres
        favorite_genres = compute_favorite_genres(collections)

        # Format the response
        response_data = {
            "is_success": True,
            "data": {
                "collections": serializer.data,
                "favourite_genres": favorite_genres,
            },
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request):
        """API to create collection"""

        # Validate incoming data using the serializer
        serializer = CollectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Perform the creation within a database transaction
        with transaction.atomic():
            # Save the collection instance using the custom create method
            collection = serializer.save(user=request.user)

        # Prepare the custom response with the collection UUID
        response_data = {
            "collection_uuid": str(collection.uuid)  # Convert UUID to string
        }

        # Return the custom response with status code 201
        return Response(response_data, status=status.HTTP_201_CREATED)


class CollectionRetrieveUpdateDestroyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, collection_uuid):
        """API to fetch the collection details by its uuid"""
        # Get the collection for the authenticated user
        collection = get_object_or_404(
            Collection, uuid=collection_uuid, user=request.user
        )
        serializer = CollectionSerializer(collection)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, collection_uuid):
        """API to update the collection by its uuid"""
        # Get the collection for the authenticated user
        collection = get_object_or_404(
            Collection, uuid=collection_uuid, user=request.user
        )
        # Validate incoming data using the serializer
        serializer = CollectionSerializer(collection, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Perform the update within a database transaction
        with transaction.atomic():
            # Extract movies data from the validated data
            movies_data = serializer.validated_data.pop("movies", None)
            # Save the collection instance with the authenticated user
            collection = serializer.save(user=request.user)

            if movies_data:
                # Clear existing movies and add new ones
                collection.movies.clear()
                for movie_data in movies_data:
                    # Either get the existing movie or create a new one
                    movie, created = Movie.objects.get_or_create(
                        uuid=movie_data["uuid"], defaults=movie_data
                    )
                    # Add the movie to the collection
                    collection.movies.add(movie)

        # Prepare the custom response with the collection UUID
        response_data = {
            "message": "Collection is updated successfully",
            "collection_uuid": str(collection.uuid),  # Convert UUID to string
        }

        # Return the custom response with status code 200
        return Response(response_data, status=status.HTTP_200_OK)

    def delete(self, request, collection_uuid):
        """API to delete the collection by its uuid"""

        # Get the collection for the authenticated user
        collection = get_object_or_404(
            Collection, uuid=collection_uuid, user=request.user
        )
        # Delete the collection
        collection.delete()
        # Return a response with status code 204
        return Response(
            data={"message": "Collection is deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


# API to get request count
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def request_count(request):
    count = RequestCount.get_count()
    return Response({"requests": count})


# API to reset request count
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reset_request_count(request):
    RequestCount.reset_count()
    return Response({"message": "request count reset successfully"})
