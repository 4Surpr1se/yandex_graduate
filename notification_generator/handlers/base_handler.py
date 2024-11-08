class BaseHandler:
    def handle(self, message):
        raise NotImplementedError("Handler must implement the handle method")
