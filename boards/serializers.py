from rest_framework import serializers

from boards.models import PostModel, CommentModel


class PostModelSerializer(serializers.ModelSerializer):
    # BoardModel 에 정의하지 않은 새로운 필드 (해당 게시글의 댓글 수)
    comment_num = serializers.SerializerMethodField()

    # get_{fields 이름}
    def get_comment_num(self, obj):
        comment_num= obj.post_comment.count() # related_name 으로 역참조
        return comment_num

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

    def update(self, instance, validated_data):
        # 업데이트시 owner 필드 제외
        validated_data.pop('owner', None)
        return super().update(instance, validated_data)
    

class CommentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentModel
        fields = '__all__'
    
    # 필드의 표현 방식 변환 id => username
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['owner'] = instance.owner.username
        return representation
    
    def update(self, instance, validated_data):
        # 업데이트시 owner, board 필드 제외
        validated_data.pop('owner', None)
        validated_data.pop('board', None)
        return super().update(instance, validated_data)