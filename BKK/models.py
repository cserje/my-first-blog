from django.db import models

COMMAND_CHOICES = sorted([("UP","PERIODIC_UPDATE"), ("RQ","VEHICLE_LIST_REQUEST"), ("CO","VEHICLE_CONFIRMATION")])
MODE_CHOICES = sorted([("IN_VEHICLE","IN_VEHICLE"), ("ON_BICYCLE","ON_BICYCLE"), ("ON_FOOT","ON_FOOT"), ("RUNNING","RUNNING"), ("STILL","STILL"), ("TILTING","TILTING"), ("UNKNOWN","UNKNOWN"), ("WALKING","WALKING")])


class LocationReport(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    userId = models.BigIntegerField()
    locationTs =  models.BigIntegerField()
    command = models.CharField(choices=COMMAND_CHOICES,max_length=30)
    lat = models.FloatField(blank=True,null=True)
    lon = models.FloatField(blank=True,null=True)
    cellTs = models.BigIntegerField(blank=True,null=True)
    cid = models.TextField(blank=True,null=True)
    mcc = models.PositiveSmallIntegerField(blank=True,null=True)
    mnc = models.PositiveSmallIntegerField(blank=True,null=True)
    accuracy = models.IntegerField(blank=True,null=True) #float?
    mode = models.CharField(choices=MODE_CHOICES,max_length=20,blank=True)
    confidence = models.IntegerField(blank=True,null=True) #float?
    vehicleId = models.TextField(blank=True)

    class Meta:
        ordering = ('created',)
