from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from ..serializer import RegisterSerializer, LoginSerializer


User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Đăng ký thành công!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Thiếu refresh token!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message" : "Đăng xuất thành công!"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Token không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        # Validate required fields
        if not current_password or not new_password:
            return Response(
                {"error": "Vui lòng cung cấp mật khẩu hiện tại và mật khẩu mới"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate password minimum length
        if len(new_password) < 6:
            return Response(
                {"error": "Mật khẩu mới phải có ít nhất 6 ký tự"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify current password
        if not user.check_password(current_password):
            return Response(
                {"error": "Mật khẩu hiện tại không đúng"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set and save new password
        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Thay đổi mật khẩu thành công"},
            status=status.HTTP_200_OK
        )


# Add to api/views/user_view.py
class CheckUserRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'is_customer': user.is_customer,
            'is_staff': user.is_staff_member,
            'is_admin': user.is_admin_user,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        return Response(data)