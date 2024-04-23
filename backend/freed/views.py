from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render
from dotenv import load_dotenv
import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta, timezone
import json
from rest_framework.parsers import JSONParser

load_dotenv()

moralis_api_key = os.getenv('MORALIS_APIKEY')

def my_profile(request):
    return render(request, 'profile.html', {})

def moralis_auth(request):
    return render(request, 'login.html', {})

class SendChallengeView(APIView):
    """
    Using Moralis, set up a view that sends a challenge to the frontend.
    """

    def post(self, request):
        # print(moralis_api_key)
        # print(request.data)
        # Set challenge deadline
        present = datetime.now(timezone.utc)
        present_plus_one_m = present + timedelta(minutes=1)
        expirationTime = str(present_plus_one_m.isoformat())
        expirationTime = str(expirationTime[:-6]) + 'Z'

        # Moralis Authentication API
        REQUEST_URL = 'https://authapi.moralis.io/challenge/request/evm'

        # Assuming 'data' is coming from the request body
        data = request.data

        request_object = {
            "domain": "defi.finance",
            "chainId": 1,
            "address": data['address'],
            "statement": "Please confirm",
            "uri": "https://defi.finance/",
            "expirationTime": expirationTime,
            "notBefore": "2020-01-01T00:00:00.000Z",
            "timeout": 15
        }

        try:
            x = requests.post(
                REQUEST_URL,
                json=request_object,
                headers={'X-API-KEY': moralis_api_key})

            # print(x)

            if x.status_code in [200, 201]:
                return Response(json.loads(x.text), status=status.HTTP_200_OK)
            else:
                return Response(json.loads(x.text), status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyMessageView(APIView):
    """
    Verifies a message using Moralis and handles user authentication.
    """

    def post(self, request):
        # The commented codes are Testing purpose. Do not Test in Production

        # print(request.data)

        # # Parse JSON data from request using DRF's JSONParser
        # parser = JSONParser()
        # try:
        #     data = parser.parse(request)
        # except Exception as e:
        #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        data = json.loads(request.body)
        print(data)

        REQUEST_URL = 'https://authapi.moralis.io/challenge/verify/evm'

        try:
            x = requests.post(
                REQUEST_URL,
                json=data,
                headers={'X-API-KEY': moralis_api_key})

            print(x.status_code)
            print(x.text)
            print(json.loads(x.text).get('address'))

            if x.status_code in [200, 201]:
                # User can authenticate
                eth_address = json.loads(x.text).get('address')
                try:
                    user = User.objects.get(username=eth_address)
                except User.DoesNotExist:
                    user = User(username=eth_address)
                    user.is_staff = False
                    user.is_superuser = False
                    user.save()

                if user is not None and user.is_active:
                    login(request, user)
                    request.session['auth_info'] = data
                    request.session['verified_data'] = json.loads(x.text)
                    return Response({'user': user.username}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'account disabled'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response(json.loads(x.text), status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
science hamster hand fetch ahead relief village copper mimic valve between bacon
"""