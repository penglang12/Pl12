"""结构化错误类 - 对应 be-best-practices 的 AppError 模式。"""


class AppError(Exception):
    """所有业务异常的基类。"""

    def __init__(self, message: str, status_code: int = 500, code: str = "INTERNAL_ERROR"):
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class ValidationError(AppError):
    def __init__(self, details: str = "验证失败"):
        super().__init__(details, status_code=400, code="VALIDATION_ERROR")


class NotFoundError(AppError):
    def __init__(self, resource: str = "资源"):
        super().__init__(f"{resource} 不存在", status_code=404, code="NOT_FOUND")


class AuthError(AppError):
    def __init__(self, message: str = "未授权"):
        super().__init__(message, status_code=401, code="UNAUTHORIZED")


class ApiError(AppError):
    """外部 API 调用异常。"""

    def __init__(self, message: str, provider: str = "unknown", status_code: int = 502):
        self.provider = provider
        super().__init__(f"[{provider}] {message}", status_code=status_code, code="API_ERROR")


class ConfigError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=500, code="CONFIG_ERROR")
