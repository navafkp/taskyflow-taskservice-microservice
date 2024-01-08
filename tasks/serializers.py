from rest_framework import serializers
from .models import (
    Boards, Columns, Card,
    Assignee, Comments, Meeting
)

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boards
        fields = [
            "user_id", "workspace", "name",
            "description", "visibility",
        ]

        def create(self, validated_data):
            board = Boards.objects.create(**validated_data)
            return board


class getAllBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boards
        fields = '__all__'


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Columns
        fields = '__all__'

        def create(self, validated_data):
            columns = Columns.objects.create(**validated_data)
            return columns


class getAllColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Columns
        fields = '__all__'


class CardSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'

        def create(self, validated_data):
            card = Card(**validated_data)
            return card


class getAllCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'


class AssigneeSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Assignee
        fields = '__all__'

        def create(self, validated_data):
            assignee = Assignee(**validated_data)
            return assignee


class getAllAssigneeSerializer(serializers.Serializer):
    card_id = serializers.IntegerField()

    def to_representation(self, instance):
        return {
            'id': instance['id'],
            'user': instance['user'],
            'card': instance['card_id'],
        }


class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'

    def create(self, validated_data):
        comment = Comments.objects.create(**validated_data)
        return comment


class GetCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'


class MeetingSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'

    def create(self, validated_data):
        """Create and return a new Meeting instance."""
        return super().create(validated_data)


class GetMeetingSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'
