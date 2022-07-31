from flask import current_app, request
import typing as t


class Log:
    @staticmethod
    def warning(msg: t.Any) -> None:
        current_app.logger.warning(request.remote_addr + '  ' + str(msg))

    @staticmethod
    def error(msg: t.Any) -> None:
        current_app.logger.error(request.remote_addr + '  ' + str(msg))

    @staticmethod
    def exception(e: Exception) -> None:
        current_app.logger.exception(request.remote_addr + '  ' + str(e))
