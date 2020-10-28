from django.core.management.base import BaseCommand
from drrr.repositories.UserRepository import UserRepository
from drrr.repositories.RoomRepository import RoomRepository
from datetime import datetime, timedelta, date
from django.utils import timezone, timesince


class Command(BaseCommand):

    def handle(self, *args, **options):
        params = {'created_at__lt': timezone.now() + timedelta(days=-1)}
        UserRepository.delete(params=params)
        RoomRepository.delete(params=params)




