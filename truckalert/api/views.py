from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from api.serializers import PositionSerializer
from api.models import Position
import geopy.distance


class UpdatePosition(APIView):
    
    def get_pos_object(self, uid):
        try:
            return Position.objects.get(user_id=uid)
        except:
            return False
    
    def app_key_valid(self, key):
        #implement application key validation
        return True

    def post(self, request, format=None):

        app_key = request.data['app_key']

        if not self.app_key_valid(app_key): #check validity of the application key
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

        uid = request.data['data']['user_id']
        pos_object = self.get_pos_object(uid)
        serializer = PositionSerializer(data=request.data['data'])

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if pos_object: #if the user is already registered
            serializer2 = PositionSerializer(pos_object, data=request.data['data'])
            if not serializer2.is_valid():
                return Response(seiralizer2.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            serializer2.save()
            
        else:
            serializer.save()
       
        new_long = request.data['data']['new_long']
        new_lat = request.data['data']['new_lat']
        search_radius = 200 #scope of search in meters 

        alerts = Position.objects.raw('SELECT * FROM api_position WHERE alert=true')
        alert_positions = []
        for pos in alerts:
            if geopy.distance.distance((pos.new_lat, pos.new_long), (new_lat, new_long)).m <= 200:
                alert_positions.append({"longitude": pos.new_long, "latitude": pos.new_lat})
        return Response(alert_positions)

    
    def get(self, request, format=None):
        return Response("TEST SUCCESSFUL")
