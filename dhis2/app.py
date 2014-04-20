from rapidsms.apps.base import AppBase
from rapidsms.router import get_router
import operations

class PingPong(AppBase):
    def handle(self, message):
        op_codes = operations.get_associated_operation_codes("dhis2", "PingPong")
        if message.operation_code in op_codes:
            message.respond("pong: %s" % str(message.arguments))
        return False
get_router().add_app(PingPong)

operations.register("dhis2", "PingPong", operations.Syntax())