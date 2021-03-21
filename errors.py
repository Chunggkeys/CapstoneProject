class Error:
    def __init__(self, message):
        self.message = message

    def message(self):
        return self.message

class SampleError(Error):
    def __init__(self, message):
        super(SampleError, self).__init__(message)

class ActuatorError(Error):
    def __init__(self, message):
        super(ActuatorError, self).__init__(message)

class CircuitError(Error):
    def __init__(self, message):
        super(CircuitError, self).__init__(message)

class DatabaseError(Error):
    def __init__(self, message):
        super(DatabaseError, self).__init__(message)

class WifiError(Error):
    def __init__(self, message):
        super(WifiError, self).__init__(message)

class EnclosureError(Error):
    def __init__(self, message):
        super(EnclosureError, self).__init__(message)