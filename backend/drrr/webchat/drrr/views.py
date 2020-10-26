from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drrr.models import users, room
import json
from django.db import connection
from drrr.repositories.UserRepository import UserRepository


@csrf_exempt
def login(request):
    if request.method == 'GET':
        return JsonResponse({'status': 'FAIL', 'message': 'Method not allow.'})
    try:
        params = json.loads(request.body.decode())
        insert_data = {
            'nickname': params['nickname'],
            'avatar': params['avatar']
        }
        user = UserRepository.store(insert_data=insert_data)
    except TypeError as e:
        return JsonResponse({'status': 'FAIL', 'message': str(e)})
    return JsonResponse({'status': 'SUCCESS', 'uuid': user.uuid})


@csrf_exempt
def room_list(request):
    params = json.loads(request.body.decode())
    uuid = params['uuid']
    user = users.objects.filter(uuid=uuid).first()
    if not user:
        return JsonResponse({'status': 'FAIL', 'message': 'User not found'})

    with connection.cursor() as cursor:

        raw_sql = 'SELECT r.id, r.name,r.max_member,r.host_nickname, count(u.join_room_id) curr_member ' \
                  'FROM drrr_room r JOIN drrr_users u ON u.join_room_id = r.id ' \
                  'WHERE r.deleted_at IS null ' \
                  'GROUP BY u.join_room_id'
        cursor.execute(raw_sql)

        ret_data = query_set_to_dict(cursor)
    return JsonResponse({'status': 'SUCCESS', 'data': ret_data})


def query_set_to_dict(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

