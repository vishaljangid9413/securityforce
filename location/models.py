from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = ("Country")
        verbose_name_plural = ("Countries")

class State(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = ("State")
        verbose_name_plural = ("States")       

class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = ("City")
        verbose_name_plural = ("Cities")

class Zipcode(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    zipcode = models.CharField(max_length=20)

    def __str__(self):
        return self.city.name

    class Meta:
        verbose_name = ("Location")
        verbose_name_plural = ("Locations")