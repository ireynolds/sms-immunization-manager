from register import define_operation_code, associate_operation_code

# Define how operation codes map to operations here
define_operation_code("ping", "dhis2", "PingPong")
associate_operation_code("ping", "notifications", "TestMultipleHandlers")