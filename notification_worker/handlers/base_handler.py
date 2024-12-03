class BaseNotificationHandler:
    def send(self, data, properties):
        raise NotImplementedError("Must override send method")