from rest_framework import serializers

from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    # 클라이언트들에게 전달 x
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username', 'fullname')

    # User 객체 생성
    # CRUD 중 Create 함수 오버라이딩
    def create(self, validated_data):
        # 여기서는 자동으로 비밀번호를 hashing 하여 저장함.
        instance = User.objects.create_user(
            email= validated_data['email'],
            username= validated_data['username'],
            password= validated_data['password'],
            fullname= validated_data['fullname'])
        
        return instance
    
    # Update 함수 오버라이딩
    def update(self, instance, validated_data):
        # patch 를 위해 key값이 있는 필드별로 업데이트
        for key, value in validated_data.items():
            # User 정보 수정시 비밀번호는 hashing 하여 저장해야함.
            if key == "password":
                instance.set_password(value)

            else:
                setattr(instance, key, value)

        instance.save()
        return instance
