from django.db import models

class Tabless(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500, default="name", unique=True)

    def __str__(self):
        return self.name


class Rows(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    Tables = models.ForeignKey(Tabless, on_delete=models.CASCADE)
    Teilindikator = models.CharField(max_length=500, blank=True, null=True)
    Datenquelle = models.CharField(max_length=500, blank=True, null=True)
    Code= models.CharField(max_length=500, blank=True, null=True)
    Datum = models.DateField(blank=True, null=True)
    Status = models.CharField(max_length=500, default="Active")
    Wert = models.CharField(null=True, blank=True,max_length=500)
    Top3 = models.IntegerField(null=True, blank=True)
    EUDurchschnitt = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.Teilindikator
