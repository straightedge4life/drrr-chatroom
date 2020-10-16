from django.db import models
import datetime
import uuid

class users(models.Model):
    uuid = models.CharField(max_length=255, null=True)
    channel_name = models.CharField(max_length=255, null=True)
    nickname = models.CharField(max_length=50, default='john due')
    avatar = models.SmallIntegerField(default=1)
    join_room_id = models.IntegerField(default=0)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def delete(self):
        self.save(deleted_at=datetime.datetime.now())

    @classmethod
    def create(cls, **kwargs):
        kwargs['uuid'] = str(uuid.uuid4())
        return cls.objects.create(**kwargs)


class room(models.Model):
    name = models.CharField(max_length=100)
    max_member = models.SmallIntegerField()
    host_id = models.IntegerField()
    host_nickname = models.CharField(max_length=50, default='john due')
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def delete(self):
        self.save(deleted_at=datetime.datetime.now())
