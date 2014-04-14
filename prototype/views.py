from models import *
from django.shortcuts import render_to_response, get_object_or_404

def home(request):
    roots = HeirarchyNode.objects.filter(parent=None)
    moderations = Message.objects.filter(user__heirarchy_node=None, moderation_hold=True)
    return render_to_response("home.html", {'roots': roots, 'moderations': moderations})

def node(request, node_pk):
    node_model = get_object_or_404(HeirarchyNode, pk=node_pk)
    return render_to_response("node.html", {'node': node_model})

def message(request, message_pk):
    message_model = get_object_or_404(Message, pk=message_pk)
    return render_to_response("message.html", {'message': message_model})

def user(request, user_pk):
    message_model = get_object_or_404(PhoneUser, pk=user_pk)
    return render_to_response("user.html", {'user': user_model})