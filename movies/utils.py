from collections import Counter

from movies.models import Movie


def compute_favorite_genres(collections):
    # Collect all movies from all collections
    movies = Movie.objects.filter(collections__in=collections).distinct()

    # Aggregate genres from all movies
    genres = []
    for movie in movies:
        if movie.genres:
            genres.extend(movie.genres.split(','))

    # Count the occurrences of each genre
    genre_counts = Counter(genres)

    # Get the top 3 genres
    top_genres = [genre for genre, count in genre_counts.most_common(3)]

    # Return as a comma-separated string
    return ', '.join(top_genres)