from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
from drrr.models import users, room
from asgiref.sync import async_to_sync
import datetime


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
                self.send_msg_to_room(text_data_json)

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
            user = self.find_user_by_channel_name(channel_name=channel_name)

            # 用户是否已经加入房间 若是则向房间推送退出
            if user.join_room_id:
                self.send_notify_to_room(user.join_room_id, user.nickname+' offline.')
                self.channel_group_exit(user.join_room_id)

            # async_to_sync(self.channel_layer.group_discard)(str(user.join_room_id), self.channel_name)
            # async_to_sync(self.channel_layer.group_discard)("0", self.channel_name)
            users.objects.filter(channel_name=channel_name).update(join_room_id=0)

        except Exception as e:
            err_info = {
                'type': 'error',
                'message': str(e)
            }
            print('error：'+str(e))
            print('------------------')
            # self.send(text_data=json.dumps(err_info))

    @staticmethod
    def find_user_by_uuid(uuid: str):
        """
        根据UUID查找用户
        查不到会抛出异常
        :param uuid:
        :return:
        """
        user = users.objects.filter(uuid=uuid, deleted_at=None).first()
        if not user:
            raise Exception('Not allow to create chat room for this user')

        return user

    @staticmethod
    def find_user_by_channel_name(channel_name: str):
        user = users.objects.filter(channel_name=channel_name).first()
        if not user:
            raise Exception('User not found.')
        return user

    @staticmethod
    def find_room_by_id(room_id: int):
        """
        根据ID查找房间
        查不到抛出异常
        :param room_id:
        :return:
        """
        room_info = room.objects.filter(id=room_id, deleted_at=None).first()
        if not room_info:
            raise Exception("Room not found.")

        room_info.curr_member = users.objects.filter(join_room_id=room_info.id).count()
        return room_info

    @staticmethod
    def room_member_check(room_id):
        """
        检查房间人数 为0则删除房间
        :param room_id:
        :return:
        """
        room_member = users.objects.filter(join_room_id=room_id).count()
        if not room_member:
            room.objects.filter(id=room_id).update(deleted_at=datetime.datetime.now())

    def user_bind(self, uuid: str):
        """
        将channel_name绑定到用户信息中
        :param uuid:
        :return:
        """
        # 验证用户
        user = self.find_user_by_uuid(uuid=uuid)
        users.objects.filter(id=user.id).update(channel_name=self.channel_name)

        # 加入到公共频道
        self.channel_group_join(0)

    def room_create(self, data: dict):
        """
        创建房间
        :param data:
        :return:
        """

        # 查找用户，不允许重复创建房间
        user = self.find_user_by_uuid(data['uuid'])
        if user.join_room_id > 0:
            raise Exception('Not allow to create chat room for this user')

        # 整理下数据，然后入库并更新用户信息
        data.pop('type')
        data.pop('uuid')
        data['host_id'] = user.id
        data['host_nickname'] = user.nickname

        room_info = room.objects.create(**data)
        users.objects.filter(uuid=user.uuid).update(join_room_id=room_info.id)

        # 到channel创建房间并加入
        self.channel_group_join(room_id=room_info.id)

        # 向房间发送入房提醒
        self.send_notify_to_room(room_id=room_info.id, content=user.nickname+" created this room.")

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
        user = self.find_user_by_uuid(uuid)

        # # 用户当前进入的房间与传过来的房间ID不对应,包含了用户未进任何房间
        # if user.join_room_id != data['room_id']:

        # 用户已经进入其他房间(切房)
        if user.join_room_id:
            self.channel_group_exit(user.join_room_id)

        # 查找房间信息
        room_info = self.find_room_by_id(room_id)
        if room_info.curr_member >= room_info.max_member:
            raise Exception('Room is full')

        # 更新用户信息
        users.objects.filter(id=user.id).update(join_room_id=room_info.id)

        # 加入房间(channels)
        self.channel_group_join(room_id=room_info.id)

        # 向公共频道发送信息
        self.send_sys_msg('room_list')

        # 向房间发送入房提醒
        self.send_notify_to_room(room_id=room_info.id, content=user.nickname + " has joined this room.")

        self.send(text_data=json.dumps({
            'id': room_info.id,
            'name': room_info.name,
            'max_member': room_info.max_member,
            'curr_member': room_info.curr_member,
            'host_id': room_info.host_id
        }))

    def exit_room(self, uuid: str):
        """
        用户退出当前房间
        :param uuid:
        :return:
        """

        user = self.find_user_by_uuid(uuid=uuid)

        async_to_sync(self.channel_layer.group_discard)(str(user.join_room_id), self.channel_name)

        users.objects.filter(uuid=uuid).update(join_room_id=0)

        # 检查剩余人数(mysql)
        self.room_member_check(room_id=user.join_room_id)

        # 向公共频道发送信息
        self.send_sys_msg('room_list')

        # 向房间发送入房提醒
        self.send_notify_to_room(room_id=user.join_room_id, content=user.nickname + " has left this room.")

        # 返回数据，无意义
        self.send(text_data=json.dumps({'status': 'SUCCESS'}))

    def send_msg_to_room(self, data: dict):
        """
        向房间内所有成员发送消息
        :param data:
        :return:
        """
        user = self.find_user_by_uuid(data['uuid'])
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

    def send_notify_to_room(self, room_id: int, content: str):
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
        user = self.find_user_by_channel_name(channel_name=self.channel_name)
        print(user)

        # 退出公共频道
        self.channel_group_exit(room_id=0)

        # 如果有正在进入的房间，先退出
        if user.join_room_id:
            self.channel_group_exit(user.join_room_id)
            self.room_member_check(room_id=user.join_room_id)
            self.send_sys_msg('room_list')

        # 删除用户
        users.objects.filter(uuid=user.uuid).update(deleted_at=datetime.datetime.now())

################ 需要测试 #################

# 1. self.channel_layer.group_add 是否没则创建
# 2. self.channel_layer.group_discard 是否只是当前用户退出
# 3. 用户已经进入组的情况下， 能否不group_discard直接group_add切换到其他房间
# 4. 房间列表更新推送思路: 若用户进入到列表页时，先统一加入到一个公共的common组，
#    如果有房间要销毁时，则推送至common组通知向api拉取最新房间列表数据
#    后续如果进行创建/进入房间等操作，再切换到其他组

# 1. yes
# 2. yes 全部人退出后即删除房间
# 3. 可以，但两间房都会存在该channel_name


#  2020 09 28记录
# 1. 已解决vue的请求与Django无法接收json问题
#   1.1 请求组件用axios
#   1.2 Django接收json需要使用request.body.decode() 再使用json.dumps()解析
#
# 2. vue的websocket
#   2.1 websocket在全局Vue变量中进行连接
#   2.2 如果B需要向S推送直接在当前vue文件写this.ws.send()
#   2.3 如果(B需要接收推送可以再当前vue文件写this.ws.onmessage = function){}
#   2.4 但未知2.3的onmessage方法是否能在不同vue文件被重写 (可以)

# 3. 因为数据库不记录聊天信息，而Django单纯将信息接收与群发到组内成员，故B接收消息时无法标识消息发送者 (已解决)
#   3.1 在后端接收到ws的信息时，如果type为message，在转发到组内成员前先将发送者信息封装到内容中(json)
#   3.2 发送者信息包含nickname、avatar、content，前端解析并展示 ()

# 20200930
# 1.vue
#   1.1 因为在main.js实例化的ws并打入到Vue.ws(vue文件的this.ws),用户在刷新页面后将出现其他vue页面的this.ws为undefined的问题
#   尝试过判断this.ws == undefined 时重新实例化ws并打入到this.ws，会报错

# 2.django
#   2.1 在api:room_list里，使用了raw sql，但最终出来结果缺少了count(u.id) as curr_member一项，可以说整个select都失效
#       但后面的条件都生效了 有可能是因为models.py未定义该字段?  但尝试select少几个字段出来的结果也是全部字段
# https://docs.djangoproject.com/zh-hans/3.1/topics/db/sql/#executing-custom-sql-directly
# 已解决 等前端稍作修改  格式改为如下
# {
#     "status": "SUCCESS",
#     "data": [
#         {
#             "id": 5,
#             "name": "nnnn",
#             "max_member": 10,
#             "host_nickname": "john due",
#             "curr_member": 1
#         }
#     ]
# }

#  bug 2020 10 13
# 1.在边操作、边刷新的测试中，最后无论在公共频道(0)还是用户创建频道，都会遗留之前的channel_name,需要先从公共频道下手
#   1.1 只要在创建房间时刷新、再创建房间、再退出房间时会出现
