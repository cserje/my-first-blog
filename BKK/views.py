import os

from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
import requests, json
import sys
from subprocess import Popen
import subprocess
import json
from pprint import pprint
import shutil
from operator import itemgetter

class VehicleListRequest(generics.CreateAPIView):




    def post(self, request):
        if request.POST.get('command') and request.POST.get('command') == 'RQ':



            # userid=request.POST.get('userId')
            # i = 0
            # max_lines = 0
            # a = subprocess.check_output('./segmentation.sh %s' % (str(userid)), shell=True)
            #
            # # splitting the string to count the lines and get the temp location
            # for line in a.split('\n'):
            #     i += 1
            #     max_lines = i
            # path = ""
            # i = 0
            # for line in a.split('\n'):
            #     if (i == max_lines - 2):  # -2: empty line and EOF split (maybe)
            #         path = line
            #     i += 1
            # file_directory = path + '/correlated_segments_gps.json'
            file_directory='D:\Documents\Django\BKK\BKK\correlated_segments_gps.json'

            print(file_directory)

            with open(file_directory) as data_file:
                data = json.load(data_file)  # TODO: if there is no json file

            # segedindex lista, a nem kivanatos elemeket majd ennek segitsegevel dobaljuk ki
            indexes = []
            l = 0
            for path_segment_list in data['path_segment_list']:
                if path_segment_list["deviations"]:
                    sum = 0  # segedvaltozok az atlagolashoz
                    i = 0
                    for deviations in path_segment_list["deviations"]:
                        sum = sum + deviations['relative']
                        i = i + 1
                    path_segment_list['path_segment']['avg_deviation'] = sum / i
                    latest_location_ts = 0
                    for points in path_segment_list['path_segment'][
                        'points']:  # szuksegunk van a legkesobbi ts-re, hogy ugyanazon jarmurol kidobalhassuk a regebbi bejegyzeseket
                        latest_location_ts = points['ts']
                    path_segment_list['path_segment']['segment_last_ts'] = latest_location_ts
                else:
                    indexes.append(
                        l)  # if <lista>: hamissal ter vissza, ha ures, ebben az esetben a segedlistahoz hozzaadjuk a megfelelo indexet
                l += 1

            # a kinyert indexeken levo elemeket toroljuk, ugyelve arra, hogy az indexek valtoznak torles eseten
            correction = 0
            for var in indexes:
                data['path_segment_list'].pop(var - correction)
                correction += 1

            # kivesszuk a tobbszor szereplo jarmuvek kozul a regebbieket, ehhez segedvaltozokat hasznalunk
            dict = {}
            i = 1  # azert 1-rol kezdjuk, mert hatulrol jarjuk be a listat, igy a listameret-i az elso lepesben mar az utolso elemre mutat
            indexes = []  # a szamunkra nem kivanatos elemek indexei ide kerulnek
            for path_segment_list in data['path_segment_list'][::-1]:  # forditott sorrendben lepkedunk
                if path_segment_list['path_segment'][
                    'vehicle_id'] in dict:  # ha benne a vehicle_id kulcskent szerepel a listaban
                    if path_segment_list['path_segment']['segment_last_ts'] <= dict[
                        path_segment_list['path_segment']['vehicle_id']]:
                        indexes.append(len(data['path_segment_list']) - i)
                else:  # ha nem kulcs a vehicle_id a listaban, akkor belerakjuk
                    dict[path_segment_list['path_segment']['vehicle_id']] = path_segment_list['path_segment'][
                        'segment_last_ts']
                i = i + 1

            # elemek torlese index szerint
            correction = 0
            for var in indexes:
                data['path_segment_list'].pop(var - correction)
                correction += 1

            # a nem szukseges dolgok kidobalasa, illetve a deviation kulcs szerint rendezes
            list = []
            for var in data['path_segment_list']:
                var['path_segment'].pop('max_distance', None)
                var['path_segment'].pop('points', None)
                var['path_segment'].pop('duration', None)
                list.append(var['path_segment'])

            list = sorted(list, key=itemgetter('avg_deviation'))
            print(list)

            #queryset = self.get_queryset(request)
            # szukseges=queryset['data']['list']
            # for szuksegesadat in list:
            # #Ha van tripId kulcsa a szurt listanak
            #     if 'tripId' in szuksegesadat:
            #         #iterálunk az eredeti lista trips-jen belül
            #         for var in queryset['data']['references']['trips']:
            #             if 'id' in var:
            #                 if szuksegesadat['tripId']==var['id']:
            #                     szuksegesadat['tripHeadsign']=var['tripHeadsign']
            #print(path)
            # shutil.rmtree(path)









            papa={'data':4, 'adat':5}
            papa['imsi']=request.POST.get('userId')
            return JsonResponse(list,safe=False)

            #return JsonResponse(queryset['data']['list'],safe=False) #serializer.data)
        else:
            return Response(request.POST)

    def get_queryset(self, request):
        return self.get_vehicle_list_from_bkk(request)

    def get_vehicle_list_from_bkk(self, request):
        vehicles_request = 'http://futar.bkk.hu/bkk-utvonaltervezo-api/ws/mobile/api/where/vehicles-for-location.json?key=bkk-android&appVersion=2.0.3&lat=%(lat)s&lon=%(lon)s&latSpan=%(latspan)s&lonSpan=%(lonspan)s' % {'lat':request.POST.get('lat') , 'lon':request.POST.get('lon'), 'latspan':2, 'lonspan':2}
        headers = {'user-agent': 'BKK-Android/2.1.5', 'connection': 'Keep-Alive'}
        vehicles = requests.get(vehicles_request, headers=headers)
        return vehicles.json()
