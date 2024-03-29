import string
import random
import base64

user_img_lst = [
    'https://img.zcool.cn/community/01a12c576cd97e0000012e7e11b4f0.png@1280w_1l_2o_100sh.png',
    'https://img.zcool.cn/community/01e61d576cd97d0000018c1bc49d87.png@1280w_1l_2o_100sh.png',
    'https://img.zcool.cn/community/01bc52576cd97d0000012e7ecbb17b.png@1280w_1l_2o_100sh.png',
    'https://img.zcool.cn/community/01ce5c576cd97f0000012e7eeae7be.png@1280w_1l_2o_100sh.png',
    'https://img.zcool.cn/community/018f59576cd97f0000012e7e9e3ac3.png@1280w_1l_2o_100sh.png'
]

title_img_lst = [
    'https://st-gdx.dancf.com/gaodingx/0/uxms/design/20210126-103424-415b.png?x-oss-process=image/resize,'
    'h_1200/interlace,1,image/format,webp',
    'https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fst-gdx.dancf.com%2Fgaodingx%2F1570%2Farticles%2F0'
    '%2F20200918-102809-35e1.png&refer=http%3A%2F%2Fst-gdx.dancf.com&app=2002&size=f9999,'
    '10000&q=a80&n=0&g=0n&fmt=auto?sec=1660705570&t=d563595dc579b4a255bbb7db9b5920cd',
    'https://st-gdx.dancf.com/gaodingx/0/uxms/design/20210330-133751-17d9.png?x-oss-process=image/resize,'
    'w_600/interlace,1,image/format,webp',
    'https://gd-filems.dancf.com/gaoding/cms/mcm79j/mcm79j/58455/baf84a93-40db-490c-82f5-24851843a22e154759.jpg?x-oss'
    '-process=image/resize,w_600/interlace,1,image/format,webp',
    'https://gd-filems.dancf.com/gaoding/cms/mcm79j/mcm79j/73587/ad31f68c-6950-4007-853b-8e3f9fdb7b3852089.jpg?x-oss'
    '-process=image/resize,w_600/interlace,1,image/format,webp',
    'https://st-gdx.dancf.com/gaodingx/0/uxms/design/20211009-212007-19df.png?x-oss-process=image/resize,'
    'w_600/interlace,1,image/format,webp',
    'https://st-gdx.dancf.com/gaodingx/0/uxms/design/20211013-114949-dcd3.png?x-oss-process=image/resize,'
    'w_600/interlace,1,image/format,webp',
    'https://st-gdx.dancf.com/gaodingx/0/uxms/design/20201212-174749-4ba6.png?x-oss-process=image/resize,'
    'w_600/interlace,1,image/format,webp',
    'https://st-gdx.dancf.com/gaodingx/0/uxms/design/20211015-183214-bb8c.png?x-oss-process=image/resize,'
    'w_600/interlace,1,image/format,webp',
    'https://st-gdx.dancf.com/gaodingx/0/uxms/design/20210330-113547-d2b6.png?x-oss-process=image/resize,'
    'w_600/interlace,1,image/format,webp',
    'https://st-gdx.dancf.com/gaodingx/0/uxms/design/20210423-114406-5304.png?x-oss-process=image/resize,'
    'w_600/interlace,1,image/format,webp',
    'https://st-gdx.dancf.com/gaodingx/0/uxms/design/20210305-182825-4657.png?x-oss-process=image/resize,'
    'w_600/interlace,1,image/format,webp',
]


def rand_str(length: int) -> str:
    return ''.join((string.digits + string.ascii_letters)[random.randint(0, 61)] for _ in range(length))


def rand_title_img() -> str:
    return title_img_lst[random.randint(0, len(title_img_lst) - 1)]


def gen_room_id(user1_id, user2_id):
    s = max(user1_id, user2_id) + '-' + min(user1_id, user2_id)
    return base64.b64encode(s.encode()).decode()
