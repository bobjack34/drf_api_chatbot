from django.db import models


class DateMixin(models.Model):
    """abstrakte Klasse, die zwei Felder definiert, 
    die von anderen Modellen genutzt werden können.
    
    Abstrakte Klassen haben selber keine DB-Tabelle.
    """

    created_at = models.DateTimeField(auto_now_add=True) # beim Anlegen Zeitstempel
    updated_at = models.DateTimeField(auto_now=True)  # beim Update Zeitstempel

    # es wird keine Tabelle angelegt
    class Meta:
        abstract = True