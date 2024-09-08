from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .factories import UserFactory, MovieFactory, CollectionFactory
from .models import Collection


class CollectionAPITestCase(APITestCase):
    def setUp(self):
        # Set up the user
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

        # Set up some movies
        self.movie1 = MovieFactory()
        self.movie2 = MovieFactory()

    def test_create_collection(self):
        """
        Ensure we can create a new collection with movies.
        """
        url = reverse("collection-list-create")
        data = {
            "title": "My Collection",
            "description": "This is a test collection",
            "movies": [{
                "title": "Test movies",
                "description": "test",
                "genres": "comedy",
                "uuid": "aca46e95-ac03-4af2-b6a9-a7ba47da24ca"
            }
            ],
        }

        response = self.client.post(url, data, format="json")

        # Assert that the response is 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that the collection UUID is in the response
        self.assertIn("collection_uuid", response.data)

        # Assert that the collection was actually created in the database
        self.assertEqual(Collection.objects.count(), 1)
        collection = Collection.objects.get()
        self.assertEqual(collection.title, "My Collection")
        self.assertEqual(collection.movies.count(), 1)

    def test_get_collections(self):
        """
        Ensure we can retrieve collections for a user.
        """
        # Create a collection for the user
        collection = CollectionFactory(
            user=self.user, movies=[self.movie1, self.movie2]
        )

        url = reverse("collection-list-create")
        response = self.client.get(url)

        # Assert that the response is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the collection data is correct
        self.assertEqual(len(response.data["data"]["collections"]), 1)
        self.assertEqual(
            response.data["data"]["collections"][0]["title"], collection.title
        )

        # Assert that the favorite genres are correct
        self.assertIn("favourite_genres", response.data["data"])

    def test_delete_collections(self):
        """
        Ensure we can delete collection for a user.
        """
        # Create a collection for the user
        collection1 = CollectionFactory(
            user=self.user, movies=[self.movie1, self.movie2]
        )

        collection2 = CollectionFactory(
            user=self.user, movies=[self.movie1, self.movie2]
        )

        url = reverse("collection-retrieve-update-destroy", args=[str(collection2.uuid)])
        response = self.client.delete(url)

        # Check that the response status code is 204 NO CONTENT
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check that the response message is as expected
        self.assertEqual(response.data["message"], "Collection is deleted successfully")

        # Verify that the collection no longer exists in the database
        self.assertFalse(Collection.objects.filter(uuid=collection2.uuid).exists())
