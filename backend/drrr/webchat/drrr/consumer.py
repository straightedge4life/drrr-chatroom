from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from drrr.repositories.UserRepository import UserRepository
from drrr.repositories.RoomRepository import RoomRepository


class MyConsumer(WebsocketConsumer):

    def connect(self):
        print('connect.')
        print('channel_name: '+self.channel_name)
        print('----------------')
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        """
        接收信息，主要根据type来调度对应方法
        :param text_data:
        :param bytes_data:
        :return:
        """
        try:
            text_data_json = json.loads(text_data)
            print('receive')
            print(text_data_json)
            print('channel_name: '+self.channel_name)
            print('----------------')

            if text_data_json['type'] == 'bind':
                self.user_bind(uuid=text_data_json['uuid'])

            elif text_data_json['type'] == 'create':
                self.room_create(text_data_json)

            elif text_data_json['type'] == 'join':
                self.join_room(uuid=text_data_json['uuid'], room_id=text_data_json['room_id'])

            elif text_data_json['type'] == 'exit':
                self.exit_room(uuid=text_data_json['uuid'])

            elif text_data_json['type'] == 'message':
                self.send_room_message(text_data_json)

            elif text_data_json['type'] == 'exit_user':
                self.exit_user()

        except Exception as e:
            print(e.with_traceback())
            err_info = {
                'type': 'error',
                'message': str(e)
            }
            self.send(text_data=json.dumps(err_info))

    def disconnect(self, code):
        """
        用户断开链接 有可能是刷新 有可能是直接退出网页
        :param code:
        :return:
        """
        print('disconnected.')
        print('channel_name: '+self.channel_name)
        print('----------------')
        try:
            # 退出公共频道
            self.channel_group_exit(room_id=0)

            channel_name = self.channel_name
            # 根据channel name寻找用户
            params = {'channel_name': channel_name}
            user = UserRepository.find_with_exception(params=params)

            # 用户是否已经加入房间 若是则向房间推送退出
            if user.join_room_id:
                self.send_room_notify(user.join_room_id, user.nickname+' offline.')
                self.channel_group_exit(user.join_room_id)

            UserRepository.update(params=params, update_data={'join_room_id': 0})

        except Exception as e:
            err_info = {
                'type': 'error',
                'message': str(e)
            }
            self.send(text_data=json.dumps(err_info))

    def user_bind(self, uuid: str):
        """
        将channel_name绑定到用户信息中
        :param uuid:
        :return:
        """
        # 验证用户

        # 验证用户
        params = {'uuid': uuid}
        UserRepository.find_with_exception(params=params)

        UserRepository.update(params=params, update_data={'channel_name': self.channel_name})

        # 加入到公共频道
        self.channel_group_join(0)

    def room_create(self, data: dict):
        """
        创建房间
        :param data:
        :return:
        """

        # 查找用户，不允许重复创建房间
        user = UserRepository.find_with_exception(params={'uuid': data['uuid']})
        if user.join_room_id > 0:
            raise Exception('User already joined another room')

        # 整理下数据，然后入库并更新用户信息
        data.pop('type')
        data.pop('uuid')
        data['host_id'] = user.id
        data['host_nickname'] = user.nickname

        room_info = RoomRepository.store(store_data=data)
        UserRepository.update(params={'uuid': user.uuid}, update_data={'join_room_id': room_info.id})

        # 到channel创建房间并加入
        self.channel_group_join(room_id=room_info.id)

        # 向房间发送入房提醒
        self.send_room_notify(room_id=room_info.id, content=user.nickname+" created this room.")

        # 返回房间信息
        self.send(text_data=json.dumps({
            'type': 'room_create',
            'status': 'success',
            'room_id': room_info.id,
            'name': room_info.name,
            'max_member': room_info.max_member,
            'host_id': room_info.host_id,
            'host_nickname': room_info.host_nickname,
        }))

    def join_room(self, uuid: str, room_id: int):
        """
        用户进入指定房间
        :param uuid:
        :param room_id:
        :return:
        """

        # 验证用户
        user = UserRepository.find_with_exception(params={'uuid': uuid})

        # 用户已经进入其他房间(切房)
        if user.join_room_id:
            self.channel_group_exit(user.join_room_id)

        # 查找房间信息
        room_info = RoomRepository.find(params={'id': room_id})
        room_curr_member = UserRepository.count(params={'join_room_id': room_id})
        if room_curr_member >= room_info.max_member:
            raise Exception('Room is full')

        # 更新用户信息
        UserRepository.update(params={'id': user.id}, update_data={'join_room_id': room_info.id})

        # 加入房间(channels)
        self.channel_group_join(room_id=room_info.id)

        # 向公共频道发送信息
        self.send_sys_msg('room_list')

        # 向房间发送入房提醒
        self.send_room_notify(room_id=room_info.id, content=user.nickname + " has joined this room.")

    def exit_room(self, uuid: str):
        """
        用户退出当前房间
        :param uuid:
        :return:
        """

        params = {'uuid': uuid}
        user = UserRepository.find_with_exception(params=params)

        async_to_sync(self.channel_layer.group_discard)(str(user.join_room_id), self.channel_name)

        UserRepository.update(params=params, update_data={'join_room_id': 0})

        # 检查剩余人数
        RoomRepository.member_check(room_id=user.join_room_id)

        # 向公共频道发送信息
        self.send_sys_msg('room_list')

        # 向房间发送入房提醒
        self.send_room_notify(room_id=user.join_room_id, content=user.nickname + " has left this room.")

    def send_room_message(self, data: dict):
        """
        向房间内所有成员发送消息
        :param data:
        :return:
        """
        user = UserRepository.find_with_exception(params={'uuid': data['uuid']})
        if not user.join_room_id:
            raise Exception('No room joined')
        data_text = {
            'type': 'message',
            'nickname': user.nickname,
            'avatar': user.avatar,
            'content': data['content']
        }
        async_to_sync(self.channel_layer.group_send)(
            str(user.join_room_id),
            {
                "type": "send.message",
                "text": data_text,
            },
        )

    def send_room_notify(self, room_id: int, content: str):
        async_to_sync(self.channel_layer.group_send)(
            str(room_id),
            {
                "type": "send.message",
                "text": {
                    'type': 'notify',
                    'content': content
                },
            },
        )

    def send_sys_msg(self, message: str):
        """
        发送系统消息
        :param message:
        :param msg_type:
        :return:
        """
        async_to_sync(self.channel_layer.group_send)(
            "0",
            {
                "type": "send.message",
                "text": {
                    'type': 'system',
                    'content': message
                },
            },
        )

    def channel_group_join(self, room_id: int):
        async_to_sync(self.channel_layer.group_add)(str(room_id), self.channel_name)

    def channel_group_exit(self, room_id: int):
        async_to_sync(self.channel_layer.group_discard)(str(room_id), self.channel_name)

    def send_message(self, event):
        self.send(text_data=json.dumps(event['text']))

    def exit_user(self):
        # 先根据uuid查找用户
        user = UserRepository.find_with_exception(params={'channel_name': self.channel_name})

        # 退出公共频道
        self.channel_group_exit(room_id=0)

        # 如果有正在进入的房间，先退出
        if user.join_room_id:
            self.channel_group_exit(user.join_room_id)
            RoomRepository.member_check(room_id=user.join_room_id)
            self.send_sys_msg('room_list')

        # 删除用户
        # users.objects.filter(uuid=user.uuid).update(deleted_at=datetime.datetime.now())
        UserRepository.delete(params={'uuid': user.uuid})

