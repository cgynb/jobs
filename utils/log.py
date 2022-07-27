from flask import current_app, request


class Log:
    @staticmethod
    def warning(msg) -> None:
        current_app.logger.warning(request.remote_addr + '  ' + str(msg))

    @staticmethod
    def error(msg) -> None:
        current_app.logger.error(request.remote_addr + '  ' + str(msg))

    @staticmethod
    def exception(e: Exception) -> None:
        current_app.logger.exception(request.remote_addr + '  ' + str(e))
