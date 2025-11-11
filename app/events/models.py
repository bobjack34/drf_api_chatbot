from django.contrib.auth import get_user_model
from django.db import models

from project.mixins import DateMixin

User = get_user_model()  # best practice um User-Model zu importieren


class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    icon = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(
        null=True, blank=True, help_text="Beschreibung des Tags"
    )

    def __str__(self) -> str:
        return self.name


class Category(DateMixin):
    name = models.CharField(max_length=40, unique=True)  # mandatory, VARCHAR 40
    # null = darf NULLABLE in der DB, blank = darf im Formular sein
    sub_title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(
        null=True, blank=True, help_text="Beschreibung der Kategorie"
    )

    class Meta:
        # z.b. Datenbank Indizies / Constraints setze
        # DB Tablename ändern
        verbose_name = "Kategorie"
        verbose_name_plural = "Kategorien"

    def __str__(self) -> str:
        return self.name


class Event(DateMixin):

    class Group(models.IntegerChoices):
        BIG = 10, "mittelgroße Gruppe"
        SMALL = 2, "sehr kleine Gruppe"
        MEDIUM = 5, "mittelgroße Gruppe"
        LARGE = 20, "sehr große Gruppe"
        UNLIMITED = 0, "kein Limit"

    name = models.CharField(max_length=120)
    sub_title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(
        null=True, blank=True, help_text="Beschreibung der Kategorie"
    )
    date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    min_group = models.IntegerField(choices=Group.choices)  # 5, 10 oder 20
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="events"  # kino.events.all()
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="events"  # bob.events.all()
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="events",
        blank=True,
    )

    def __str__(self) -> str:
        return self.name


class Review(DateMixin):
    class Ratings(models.IntegerChoices):
        BAD = 1
        OK = 2
        COOL = 3
        GREAT = 4
        WONDERFUL = 5
        AWESOME = 6

    review = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(choices=Ratings.choices)

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"  # bob.reviews.all()
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    def __str__(self) -> str:
        return f"{self.event}: {self.rating}"
