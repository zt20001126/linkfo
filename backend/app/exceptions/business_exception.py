class BusinessException(Exception):
    """业务异常基类，用于把可预期错误转成统一、安全的 API 响应。"""

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
