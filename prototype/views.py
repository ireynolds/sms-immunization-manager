from models import *
from django.shortcuts import render_to_response, get_object_or_404

def get_moderations():
    """
    Returns a QuerySet containing all phone users that require moderation
    """
    return PhoneUser.objects.filter(message__actions__moderation_state='PENDING').distinct()

def facility_list(request):
    facilities = Facility.objects.all()
    moderations = get_moderations().filter(facility=None)
    users = PhoneUser.objects.filter(facility=None)
    return render_to_response("home.html", {'facilities': facilities,
                                            'moderations': moderations,
                                            'users': users})

def facility(request, facility_pk):
    facility_model = get_object_or_404(Facility, pk=facility_pk)
    moderations = get_moderations().filter(facility=facility_model)
    return render_to_response("facility.html", {'facility': facility_model, 'moderations': moderations})

def user(request, user_pk):
    user_model = get_object_or_404(PhoneUser, pk=user_pk)
    return render_to_response("user.html", {'user': user_model})