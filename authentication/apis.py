from django.contrib.auth import authenticate
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class GetPairTokenAPI(generics.GenericAPIView):
    permission_classes = []
    def post(self, request):
        user = authenticate(username=request.POST["username"], password=request.POST["password"])
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            response = Response()
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                secure=False,
                httponly=True,
                samesite="Strict",
                path="/auth/api/",
            )
            response.set_cookie(
                key="access_token",
                value=str(access),
                secure=False,
                httponly=True,
                samesite="Strict",
                path="/",
            )
            return response
        else:
            raise AuthenticationFailed()


class RefreshTokenAPI(generics.GenericAPIView):
    def post(self, request):
        raw_token = request.COOKIES.get("refresh_token")
        if raw_token is None:
            raise AuthenticationFailed()
        jwtauth_obj = JWTAuthentication()
        try:
            refresh_token = jwtauth_obj.get_validated_token(raw_token)
        except:
            raise AuthenticationFailed()
        access_token = refresh_token.access_token
        response = Response()
        response.set_cookie(
            key="access_token",
            value=str(access_token),
            secure=False,
            httponly=True,
            samesite="Strict",
            path="/",
        )
        return response


class Secure(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message":"hi"})
