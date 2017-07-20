from rest_framework import serializers
from BKK.models import LocationReport, COMMAND_CHOICES, MODE_CHOICES

class LocationReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocationReport
        fields = ('userId', 'locationTs', 'command', 'lat', 'lon', 'accuracy', 'cellTs', 'cid', 'mcc', 'mnc', 'mode', 'confidence', 'vehicleId')
