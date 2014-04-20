import rapidsms
from rapidsms.apps.base import AppBase
import operations

class TestMultipleHandlers(AppBase): #App(rapidsms.app.App):
    def handle(self, message):
        op_codes = operations.get_associated_operation_codes("notifications", "TestMultipleHandlers")
        if message.operation_code in op_codes:
            message.respond("Multiple handlers responded. YAY!")
        return False

operations.register("notifications", "TestMultipleHandlers", operations.Syntax())