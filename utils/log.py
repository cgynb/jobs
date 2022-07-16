from flask import current_app, request


class Log:
    @staticmethod
    def warning(msg):
        current_app.logger.warning(request.remote_addr + '  ' + str(msg))

    @staticmethod
    def error(msg):
        current_app.logger.error(request.remote_addr + '  ' + str(msg))

    @staticmethod
    def exception(e: Exception):
        current_app.logger.exception(request.remote_addr + '  ' + str(e))
