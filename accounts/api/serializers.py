from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework import exceptions
# serializer 可以用来渲染前端
# 同时也可以用来做 validation，验证一下用户的输入是否是按照要求来的

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserSerializerForTweet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
# this serializer is to validate if the request contains username and password
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class SignupSerializer(serializers.ModelSerializer):
    #ModelSerializer 最后我们可以直接 save 创建这一个用户
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    #will be called when is_validate is called
    def validate(self, data):
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'username' : 'This username address has been occupied',
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'email': 'This email address has been occupied',
            })
        return data

    def create(self, validata_data):
        username = validata_data['username'].lower()
        password = validata_data['password']
        email = validata_data['email'].lower()

        user = User.objects.create_user(
            username = username,
            password = password,
            email = email,
        )
        return user
