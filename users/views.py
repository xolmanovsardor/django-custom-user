from django.contrib.auth.models import make_password
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegisterUserSerializer
from .models import User, UserVerificationCode
from .utils import generate_otp


class RegisterView(APIView):
    def post(self, request: Request) -> Response:
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data

            user = User(
                email=validated_data['email'],
                username=validated_data['username'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
            )
            user.set_password(make_password(validated_data['password']))
            user.save()

            otp = generate_otp()

            uvc = UserVerificationCode(user=user, otp=otp)
            uvc.save()

            context = {
                'app_name': 'Django Custom User',
                'otp_code': otp,
                'year': 2026
            }

            html_message = render_to_string('otp.html', context)
            plain_message = strip_tags(html_message)
            subject = 'Tasdiqlash'
            from_email = 'holmanovsardor@gmail.com'
            to_list = [user.email]

            send_mail(
                subject,
                plain_message,
                from_email,
                to_list,
                html_message=html_message, # HTML tarkib shu yerga uzatiladi
                fail_silently=False,
            )

            return Response({'message': 'email ga kod ketti.'})
