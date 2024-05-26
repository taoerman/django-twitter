from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

"""
we can get the xx method of model instance through source=xxx
like model_instance.xxx to get data
"""
class FollowerSerializer(serializers.ModelSerializer):
    """
    serializer = Friendship.objects.filter(to_user_id=pk)
    this serializer will get all followers of pk
    for these followers, they all have followed user_id=pk,
    so they are all from_user
    """
    user = UserSerializerForFriendship(source='from_user')

    class Meta:
        model = Friendship
        # parameters in fields do not mean you have to find them in model
        # the parameters in fields should match the class attributes first
        # if there is no attribute in this class matches fields parameters
        # then, get into the model to find it.
        fields = ('user', 'created_at')

class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')

class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message' : 'from_user_id and to_user_id should be different',
            })

        # if Friendship.objects.filter(
        #     from_user=attrs['from_user'],
        #     to_user=attrs['to_user'],
        # ).exists():
        #     raise ValidationError({
        #         'message' : 'You have already followed this user',
        #     })
        return attrs

    def create(self, validated_data):
        from_user_id = validated_data['from_user_id']
        to_user_id = validated_data['to_user_id']
        return Friendship.objects.create(
            from_user_id = from_user_id,
            to_user_id = to_user_id,
        )
