# admin.py
from django.contrib import admin
from .models import Movie, Collection, RequestCount


# Register Movie Model
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    # Display all fields in the list view
    list_display = [field.name for field in Movie._meta.get_fields()]


# Register Collection Model
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    # Display all fields except ManyToManyFields in the list view
    list_display = [field.name for field in Collection._meta.get_fields() if not field.many_to_many]

    def movie_titles(self, obj):
        return ", ".join([movie.title for movie in obj.movies.all()])

    # Add the custom method to list_display
    list_display.append('movie_titles')


# Register Movie Model
@admin.register(RequestCount)
class RequestCountAdmin(admin.ModelAdmin):
    # Display all fields in the list view
    list_display = [field.name for field in RequestCount._meta.get_fields()]