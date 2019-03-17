import base64
import json

from django.contrib.auth.models import User

# Create your views here.
from django.core.management import call_command
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.contrib.rest_framework import TokenHasScope

from oauth2_provider.models import AccessToken, Application, get_access_token_model
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.signals import app_authorized
from oauth2_provider.views.mixins import OAuthLibMixin
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from .models import Modem, Station, ServiceStation
from .serializers import ModemSerializer, UserSerializer, StationSerializer, ServiceStationSerializer


class ModemList(generics.ListCreateAPIView):
    queryset = Modem.objects.all()
    serializer_class = ModemSerializer
    permission_classes = [TokenHasScope]
    required_scopes = ['modem']


class ModemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Modem.objects.all()
    serializer_class = ModemSerializer


class StationList(generics.ListCreateAPIView):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = [TokenHasScope]
    required_scopes = ['modem']


class StationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class ServiceStationList(generics.ListCreateAPIView):
    queryset = ServiceStation.objects.all()
    serializer_class = ServiceStationSerializer
    permission_classes = [TokenHasScope]
    required_scopes = ['modem']


class ServiceStationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceStation.objects.all()
    serializer_class = ServiceStationSerializer
    permission_classes = [TokenHasScope]
    required_scopes = ['modem']


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = ModemSerializer


@api_view(['GET'])  # new
@authentication_classes([])
@permission_classes([])
def api_root(request, format=None):
    return Response({
        'health': 'success',

    })
    # return Response({
    #     'users': reverse('user-list', request=request, format=format),
    #     'modems': reverse('modem-list', request=request, format=format)
    # })


@api_view(['GET'])  # new
@authentication_classes([])
@permission_classes([])
def modem_detect(request, format=None):
    call_command('detectmodems')
    return Response({
        'health': 'request send',

    })
    # return Response({
    #     'users': reverse('user-list', request=request, format=format),
    #     'modems': reverse('modem-list', request=request, format=format)
    # })


@method_decorator(csrf_exempt, name="dispatch")
class TokenView(APIView, OAuthLibMixin):
    permission_classes = (permissions.AllowAny,)
    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

    def post(self, request):

        data = request.POST
        cred_key = 'HTTP_AUTHORIZATION'
        scopes = data.get('scope')
        if cred_key not in request.META:
            if 'client_id' in data and 'client_secret' in data:
                client_id = data.get('client_id')
                client_secret = data.get('client_secret')
            else:
                return Response({'message': 'invalid client credential'}, status=404)
        else:
            client_id, client_secret = decode_credential(request.META[cred_key])

        try:
            app = Application.objects.filter(client_id=client_id).first()

            if app is not None:
                app_user = app.user
                if scopes is not None:
                    scopes = scopes.split(" ")
                    res = check_scope(scopes, app_user)
                    if not res:
                        return Response({'message': 'unauthorize'}, status=403)
            else:
                return Response({'message': 'client not found'}, status=404)
            AccessToken.objects.filter(application=app).delete()
        except Exception as e:

            return Response(str(e), status=400)
        url, headers, body, status = self.create_token_response(request)
        if status == 200:
            access_token = json.loads(body).get("access_token")
            if access_token is not None:
                token = get_access_token_model().objects.get(
                    token=access_token)
                app_authorized.send(
                    sender=self, request=request,
                    token=token)
        response = HttpResponse(content=body, status=status)

        for k, v in headers.items():
            response[k] = v
        return response


def decode_credential(auth_header):
    encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
    decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
    return decoded_credentials


def check_scope(scopes, user):
    groups = ['client', 'modem']
    k = True
    for group in groups:
        if group in scopes:
            k = k and user.groups.filter(name=group).exists()

    return k
