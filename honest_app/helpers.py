from superadmin.models import *
import os
from honest_sherpa import settings


def total_cart_item_count(request):
    cart_item = AddToCart.objects.filter(user_id=request.user.id).count()
    return cart_item


def get_size(video_size):
    # icon_path = self.not_icon
    # print(icon_path)
    # pdf_path = video_size.not_pdf
    file_size = os.path.getsize(str(settings.MEDIA_ROOT))
    formatted_float = "{:.2f}".format(file_size / 1024)
    return formatted_float
