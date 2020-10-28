from drrr.models import room
import datetime
from django.utils import timezone
from .UserRepository import UserRepository


class RoomRepository:

    @classmethod
    def find(cls, params: dict, multiple: bool = False):
        """
        根据条件查找房间
        :param params:
        :param multiple:
        :return:
        """
        params['deleted_at'] = None
        q = room.objects.filter(**params)
        if multiple:
            return q.all()
        return q.first()

    @classmethod
    def store(cls, store_data: dict):
        """
        创建房间
        :param store_data:
        :return:
        """
        return room.objects.create(**store_data)

    @classmethod
    def update(cls, params: dict, update_data: dict):
        """
        更新房间信息
        :param params:
        :param update_data:
        :return:
        """
        if not params:
            return None
        params['deleted_at'] = None

        return room.objects.filter(**params).update(**update_data)

    @classmethod
    def delete(cls, params: dict):
        """
        删除房间
        :param params:
        :return:
        """
        params['deleted_at'] = None
        return cls.update(params=params, update_data={'deleted_at': timezone.now()})

    @classmethod
    def member_check(cls, room_id: int):
        num = UserRepository.count(params={'join_room_id': room_id})
        if not num:
            return cls.delete(params={'id': room_id})


