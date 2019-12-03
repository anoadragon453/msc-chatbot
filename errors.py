class ConfigError(RuntimeError):
    """An error encountered during reading the config file

    Args:
        msg (str): The message displayed to the user on error
    """
    def __init__(self, msg):
        super(ConfigError, self).__init__("%s" % (msg,))


class BotException(BaseException):
    """An error type with a configurable message

    Args:
        msg (str): The message displayed to the user on error
    """
    def __init__(self, msg):
        self.msg = msg
        super(BotException, self).__init__()
