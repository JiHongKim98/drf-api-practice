from rest_framework import serializers

from boards.models import PostModel


class PostModelSerializer(serializers.ModelSerializer):
    # 만약 SerializerMethodField 를 통해 외래키(FK) 필드인 owner의 표현을
    # id(PK값) => username 으로 바꾸려고 한다면, SerializerMethodField 가
    # 기본적으로 read only로 설계 되어있어 'NOT NULL constraint failed'
    # 오류가 발생하게 되므로 적합하지 않다.
    # 필수 필드들은 to_representation 메소드를 사용해서 표현을 변경해야함!

    # 필드의 표현 방식 변환 id(pk) => username(str)
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['owner'] = instance.owner.username
        return representation
    

    class Meta:
        model = PostModel

        # PostModel 의 모든 필드를 사용
        fields = '__all__'

        # owner 필드를 읽기전용으로 설정하면 Create 시에도 문제.
        # 오류 => 'NOT NULL constraint failed'
        # 따라서 Update 메소드를 커스텀하여 owner 필드는 무시하도록 구현해야 한다!
        # read_only_fields = ('owner',)
    
    def update(self, instance, validated_data):
        # patch 를 위해 key값이 있는 필드별로 업데이트
        for key, value in validated_data.items():
            # key 값이 onwer 일 경우 무시
            if key != 'owner':
                setattr(instance, key, value)

        instance.save()
        return instance
    
