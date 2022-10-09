from turtle import distance
from django.shortcuts import render, get_object_or_404
from . models import Measurement
from .forms import MeasurementModelForm
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from .utils import get_geo, get_centre_coordinates, get_zoom, get_ip_address
import folium


def calculate_distance_view(request):
    #Initial values
    distance = None
    destination = None
    obj = get_object_or_404(Measurement, id=1)
    form = MeasurementModelForm(request.POST or None)
    geolocator = Nominatim(user_agent='measurements')

    ip = get_ip_address(request)
    # print(ip)
    ip = '72.14.207.99'
    country, city, lat, lon = get_geo(ip)

    location = geolocator.geocode(city)

    #Location coordinates
    l_lat = lat #Location latitude
    l_lon = lon
    pointA = (l_lat, l_lon)

    #Initial Folium map
    m = folium.Map(width=800, height=500, location=get_centre_coordinates(l_lat, l_lon), zoom_start=8)

    #Location marker
    folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'],
                icon=folium.Icon(color='purple')).add_to(m)
 

    if form.is_valid():
        instance = form.save(commit=False)
        destination_ = form.cleaned_data.get('destination')
        destination = geolocator.geocode(destination_)

        #destination cordinates
        d_lat =destination.latitude
        d_lon = destination.longitude
        pointB = (d_lat, d_lon)

        #Distance calculation
        distance = round(geodesic(pointA, pointB).km, 2)

        #folium map modification
        m = folium.Map(width=800, height=500, location=get_centre_coordinates(l_lat, l_lon, d_lat, d_lon), zoom_start=get_zoom(distance))

        #Location marker
        folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'],
                    icon=folium.Icon(color='purple')).add_to(m) 

        #destination marker
        folium.Marker([d_lat, d_lon], tooltip='click here for more', popup=destination,
                    icon=folium.Icon(color='red', icon='cloud')).add_to(m) 

        # draw a line betwwen location and destination
        line = folium.PolyLine(locations=[pointA, pointB], weight=5, color='blue')
        m.add_child(line)

        instance.location = location
        instance.distance = distance
        instance.save()

    m = m._repr_html_()
    context = {
        'distance': distance,
        'destination': destination,
        'form': form,
        'map': m,
    }
    return render(request, 'measurements/main.html', context)

