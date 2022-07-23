import string
import random


user_img_lst = [
    'https://img.zcool.cn/community/01a12c576cd97e0000012e7e11b4f0.png@1280w_1l_2o_100sh.png',
    'https://img.zcool.cn/community/01e61d576cd97d0000018c1bc49d87.png@1280w_1l_2o_100sh.png',
    'https://img.zcool.cn/community/01bc52576cd97d0000012e7ecbb17b.png@1280w_1l_2o_100sh.png',
    'https://img.zcool.cn/community/01ce5c576cd97f0000012e7eeae7be.png@1280w_1l_2o_100sh.png',
    'https://img.zcool.cn/community/018f59576cd97f0000012e7e9e3ac3.png@1280w_1l_2o_100sh.png'
]


def rand_str(length: int) -> str:
    return ''.join((string.digits + string.ascii_letters)[random.randint(0, 61)] for _ in range(length))
