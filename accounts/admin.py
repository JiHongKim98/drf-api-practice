from django.contrib import admin
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

# Scheduler 가 정상적으로 기간이 지난 토큰을 삭제하는지 확인하기 위해
# BlacklistedToken, OutstandingToken 모델을 admin 페이지에 등록
admin.register(BlacklistedToken, OutstandingToken)