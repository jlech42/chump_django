from django.contrib.auth.models import User, Group

def get_user_id_from_messenger_id(messenger_id):
    user = User.objects.get(username=messenger_id).id
    return user
