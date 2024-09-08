import factory
from django.contrib.auth.models import User
from .models import Movie, Collection
import uuid


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password123')


class MovieFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Movie

    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph', nb_sentences=3)
    genres = factory.Faker('word')
    uuid = factory.LazyFunction(uuid.uuid4)


class CollectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Collection

    user = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph', nb_sentences=2)

    @factory.post_generation
    def movies(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of movies were passed in, use them.
            for movie in extracted:
                self.movies.add(movie)
