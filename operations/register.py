# Maps an (app_name, operation_name) tuple to a syntax object
OPERATIONS = {}

# Maps an operation code to an (app_name, operation_name) tuple
OP_CODE_DEFINITIONS = {}

# Maps an (app_name, operation_name) tuple to a set of operation codes
OP_CODE_ASSOCIATIONS = {}

def register(app_name, operation_name, syntax):
    """
    Registers that app_name implements operation_name with the given syntax. operation_name is 
    an arbitrary identifier (e.g. a class name) that is unique within the given app name. If an
    operation has already been registered with the given app_name and operation_name, raises
    AlreadyRegisteredError.
    """
    key = (app_name, operation_name)

    if key in OPERATIONS:
        raise AlreadyRegisteredError("Operation '%s' from app '%s' already registered" % key)

    OPERATIONS[key] = syntax

def define_operation_code(operation_code, app_name, operation_name):
    """
    Defines the syntax of operation_code as the syntax object registered to app_name and
    operation_name. If operation_code has already been defined, raises AlreadyRegisteredError.
    """
    if operation_code in OP_CODE_DEFINITIONS:
        raise AlreadyRegisteredError("The operation code '%s' is already defined as %s" % 
                                     (operation_code, repr(OP_CODE_DEFINITIONS[operation_code])))

    OP_CODE_DEFINITIONS[operation_code] = (app_name, operation_name)
    associate_operation_code(operation_code, app_name, operation_name)

def associate_operation_code(operation_code, app_name, operation_name):
    """
    Associates operation_code with the given operation. This indicates that the given operation
    should respond to messages starting with operation_code, but does not define the syntax of
    operation_code. It is the caller's responsibility to ensure that operation_code's defined syntax
    is compatable with the given operation.
    """
    key = (app_name, operation_name)

    if key not in OP_CODE_ASSOCIATIONS:
        OP_CODE_ASSOCIATIONS[key] = set()

    OP_CODE_ASSOCIATIONS[key].add(operation_code)

def get_associated_operation_codes(app_name, operation_name):
    """
    Returns the set of operation codes associated with the given operation. If no operation codes
    have been associated with the given operation, returns an empty set.
    """
    key = (app_name, operation_name)

    if key in OP_CODE_ASSOCIATIONS:
        return OP_CODE_ASSOCIATIONS[key]

    return set()

def get_syntax(operation_code):
    """
    Returns the syntax of the given operation code. If no such operation has been defined or
    registered, raises NoSuchOperationError.
    """
    if operation_code not in OP_CODE_DEFINITIONS:
        raise NoSuchOperationError("Operation code '%s' has not been defined" % operation_code)

    key = OP_CODE_DEFINITIONS[operation_code]

    if key not in OPERATIONS:
        raise NoSuchOperationError("Operation '%s' from app '%s' has not been registered" %
                                    (key[1], key[0]))
    return OPERATIONS[key]


class AlreadyRegisteredError(Exception):
    pass

class NoSuchOperationError(Exception):
    pass