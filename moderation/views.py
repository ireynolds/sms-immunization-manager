from models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    """
    Redirects to a user's affiliated facility, or the list of root nodes if no affiliation exists.
    """
    return HttpResponseRedirect(reverse(root_nodes))

@login_required
def root_nodes(request):
    """
    Lists the root hierarchy notes
    """
    return render_to_response("root_nodes.html", context_instance=RequestContext(request))

@login_required
def node(request, node_id):
    """
    Displays a single hierarchy node
    """
    return render_to_response("node.html", context_instance=RequestContext(request))

@login_required
def facility(request, facility_id):
    """
    Displays a summary of a facility
    """
    return render_to_response("facility.html", context_instance=RequestContext(request))

@login_required
def user_summary(request, user_id):
    """
    Displays a summary of a user
    """
    return render_to_response("user_summary.html", context_instance=RequestContext(request))

@login_required
def user_edit(request, user_id):
    """
    Edits a user
    """
    return render_to_response("user_edit.html", context_instance=RequestContext(request))