from rest_framework import serializers

from application.models import SomeModel


class SomeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SomeModel
        fields = ('id', 'name')


class SomeModelUpCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = SomeModel
        fields = ('id', 'name')

    def update_or_create(self):
        id = self.validated_data.pop('id')
        name = self.validated_data.pop('name')
        instance, _ = SomeModel.objects.update_or_create(id=id, defaults={'name': name})
        return instance
