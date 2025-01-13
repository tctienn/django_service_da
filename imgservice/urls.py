from django.urls import path
from .views import get_data
from .views import post_count_product

from .views import momo_payment  # Thêm dòng này để import API thanh toán MoMo


urlpatterns = [
    path('data/', get_data, name='get_data'),
    path('post_count_product/', post_count_product, name='post_count_product'),

    path('momo_payment/', momo_payment, name='momo_payment'),  # Thêm API mới cho thanh toán MoMo

]
