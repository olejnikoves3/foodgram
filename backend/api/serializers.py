from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Follow


class FollowSerializer(serializers.ModelSerializer): 
    user = serializers.StringRelatedField( 
        default=serializers.CurrentUserDefault())  

    class Meta: 
        model = Follow 
        fields = ('user', 'following') 
        validators = [ 
            UniqueTogetherValidator( 
                queryset=Follow.objects.all(), 
                fields=['user', 'following'], 
                message='Вы уже подписаны на этого пользователя' 
            ) 
        ] 
 
    def validate_following(self, value): 
        if self.context['request'].user == value: 
            raise serializers.ValidationError( 
                'Нельзя подписываться на сомого себя') 
        return value