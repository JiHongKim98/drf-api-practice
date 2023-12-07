from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    # 현재 앱 (accounts) 가 실행될 때, 필요한 작업 정의
    def ready(self) -> None:
        from .scheduler import start
        # 1시간마다 기간지난 토큰을 삭제하는 스케쥴 start
        start()
