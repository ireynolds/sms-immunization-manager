import rapidsms
import logging
from rapidsms.apps.base import AppBase

# TODO(isaacr): Implement a parsing app here. Below is a stub.
class OperationParser(AppBase):
    def parse(self, message):
        message.operation_code = None
        message.arguments = None
        message.errors = []

        parts = message.text.split()
        if len(parts) > 0:
            op_code = parts[0]
            message.operation_code = op_code
            message.arguments = parts[1:]
        else:
            message.errors.append("Zero-length message")

    def default(self, message):
        if len(message.errors) > 0:
            message.respond("Errors: %s" % str(message.errors))
            return True
        return False