class BaseNotificationHandler:
    def send(self, data):
        raise NotImplementedError("Must override send method")