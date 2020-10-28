from drrr.models import users
from django.utils import timezone


class UserRepository:

    @classmethod
    def find(cls, params: dict, multiple: bool = False):
        """
        根据条件查找用户
        :param multiple:
        :param params:
        :return:
        """

        params['deleted_at'] = None
        q = users.objects.filter(**params)
        if multiple:
            return q.all()
        return q.first()

    @classmethod
    def find_with_exception(cls, params: dict, multiple: bool = False):
        """
       根据条件查找用户
       :param multiple:
       :param params:
       :return:
       """

        params['deleted_at'] = None
        q = users.objects.filter(**params)

        if multiple:
            data = q.all()
        else:
            data = q.first()

        if not data:
            raise Exception('User not found')

        return data

    @classmethod
    def count(cls, params: dict):
        params['deleted_at'] = None
        return users.objects.filter(**params).count()

    @classmethod
    def store(cls, insert_data: dict):
        """
        新增用户
        :param insert_data:
        :return:
        """
        return users.create(**insert_data)

    @classmethod
    def update(cls, params: dict, update_data: dict):
        """
        更新用户信息
        :param params:
        :param update_data:
        :return:
        """
        if not params:
            return None
        params['deleted_at'] = None

        return users.objects.filter(**params).update(**update_data)

    @classmethod
    def delete(cls, params: dict):
        """
        删除用户(软删除)
        :param params:
        :return:
        """
        cls.update(params=params, update_data={'deleted_at': timezone.now()})


