# Create your views here.


def home(request):
    """
    A landing page which redirects to a user's default facility.
    """
    pass

def root_nodes(request):
    """
    Lists the root hierarchy notes
    """
    pass

def node(request, node_id):
    """
    Displays a single hierarchy node
    """
    pass

def facility(request, facility_id):
    """
    Displays a summary of a facility
    """
    pass

def user(request, user_id):
    """
    Displays a summary of a user
    """
    pass