from django.urls import path
from .views import (
    RegisterUser,
    MovieListView,
    request_count,
    reset_request_count,
    CollectionListCreateAPIView,
    CollectionRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path("register/", RegisterUser.as_view(), name="register"),
    path("movies/", MovieListView.as_view(), name="movies"),
    path(
        "collection/",
        CollectionListCreateAPIView.as_view(),
        name="collection-list-create",
    ),
    path(
        "collection/<uuid:collection_uuid>/",
        CollectionRetrieveUpdateDestroyAPIView.as_view(),
        name="collection-retrieve-update-destroy",
    ),
    path("request-count/", request_count, name="request_count"),
    path("request-count/reset/", reset_request_count, name="reset_request_count"),
]
