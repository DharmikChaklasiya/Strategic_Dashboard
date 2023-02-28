from django.db import models


class Tabless(models.Model):
    name = models.CharField(primary_key=True, max_length=500, default="name")

    def __str__(self):
        return self.name


class Rows(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    Tables = models.ForeignKey(Tabless, on_delete=models.CASCADE)
    Teilindikator = models.CharField(max_length=500, blank=True, null=True)
    Datenquelle = models.CharField(max_length=500, blank=True, null=True)
    Datum = models.DateField(blank=True, null=True)
    Status = models.CharField(max_length=500, blank=True, null=True)
    Wert = models.IntegerField(null=True, blank=True)
    Top3 = models.IntegerField(null=True, blank=True)
    EUDurchschnitt = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.Teilindikator
