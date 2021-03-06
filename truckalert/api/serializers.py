from rest_framework import serializers
from api.models import Position, Event
import uuid
import math
import geopy.distance

class PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Position
        fields = ('user_id', 'new_long', 'new_lat', 'old_long', 'old_lat', 'prob_ctr', 'alert', 'last_updated')

    def check_pos(self, instance):
        refresh_rate = 30 #amount of updates sent during 1min
        precision = 8 #estimated accuracy of the position, in meters
        threshold = 5 #speed at which the vehicle is considered as having an issue, in km/h        
        geo_distance = geopy.distance.distance((instance.new_lat, instance.new_long), (instance.old_lat, instance.old_long)).m #calculate the distance between the 2 coordinates, in meters
        threshold_distance = (threshold/3.6)*(refresh_rate/60) + precision

        if geo_distance <= threshold_distance :
            return True
        elif geo_distance > threshold_distance:
            return False

    def create (self, validated_data):
        validated_data['alert'] = False
        return Position.objects.create(**validated_data)

    def update(self, instance, validated_data):
        ctr_threshold = 5 #value of prob_ctr at which an alert is given
        instance.old_long = instance.new_long
        instance.old_lat = instance.new_lat
        instance.new_long = validated_data['new_long']
        instance.new_lat = validated_data['new_lat']

        if self.check_pos(instance):
            if instance.prob_ctr <= ctr_threshold:
                instance.prob_ctr += 1
        
        else:
            if instance.alert:
                instance.alert = False

            if instance.prob_ctr > 0:
                instance.prob_ctr -= 1

        if instance.prob_ctr > ctr_threshold:
            instance.alert = True

        instance.save()
        return instance
        

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('event', 'longitude', 'latitude', 'user_id', 'date_added')
