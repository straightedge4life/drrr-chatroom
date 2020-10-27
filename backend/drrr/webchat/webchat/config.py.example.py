class Config:

    @classmethod
    def get_config(cls, name: str, default=None):
        if hasattr(cls, name):
            return getattr(cls, name)
        return default

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'db_name',
            'USER': 'db_user',
            'PASSWORD': 'db_pwd',
            'HOST': 'db_host',
            'POST': '3306',
        }
    }

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [('127.0.0.1', 6379)],
            },
        },
    }

    CORS_ALLOW_ALL_ORIGINS = True


