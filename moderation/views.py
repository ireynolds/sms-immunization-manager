from models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def home(request):
    """
    Redirects to a user's affiliated facility, or the list of root nodes if no affiliation exists.
    """
    return HttpResponseRedirect(reverse(root_nodes))

def root_nodes(request):
    """
    Lists the root hierarchy notes
    """
    return render_to_response("root_nodes.html")

def node(request, node_id):
    """
    Displays a single hierarchy node
    """
    return render_to_response("node.html")

def facility(request, facility_id):
    """
    Displays a summary of a facility
    """
    return render_to_response("facility.html")

def user_summary(request, user_id):
    """
    Displays a summary of a user
    """
    return render_to_response("user_summary.html")

def user_edit(request, user_id):
    """
    Edits a user
    """
    return render_to_response("user_edit.html")