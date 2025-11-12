from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone


def datetime_in_future(value: datetime) -> None:
    """Raise Error, wenn value in der Vergangenheit liegt."""
    if value < timezone.now() + timedelta(hours=1):
        raise ValidationError(
            "Der Zeitpunkt des Termins darf nicht in der Vergangenheit liegen"
        )
