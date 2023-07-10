# import os
# import random
# import string
#
# import nextcloud_client
#
#
# def random_str(length=6):
#     return ''.join([random.choice(string.ascii_letters) for _ in range(length)])
#
#
# def user_put_file(group_name):
#     print('----- user_put_file -----')
#     nc1 = nextcloud_client.Client('http://localhost:8080')
#     nc1.login('user1', '111111AbC*')
#
#     # makedir confirm
#     try:
#         print('file info: ', nc1.file_info('nc_img'))
#         nc1.mkdir('nc_img')
#     except nextcloud_client.nextcloud_client.HTTPResponseError as err:
#         print('err: ', err)
#         print('status_code: ', err.status_code)
#
#     # upload
#     print('put file: ', nc1.put_file('nc_img/avt.png', 'nc_img/avt.png'))
#
#     # get link
#     link_info = nc1.share_file_with_link('nc_img/avt.png')
#     print("Here is your link: " + link_info.get_link())
#
#     print('// ----- user_put_file -----')
#     return link_info.get_link()
#
#
# def normal_display_func():
#     nc = nextcloud_client.Client('http://localhost:8080')
#     nc.login('admin', '111111')
#
#     # nc.create_user(user_name='user1', initial_password='111111AbC*')
#
#     # management user & group
#     print('Get user: ', nc.get_users())
#     print('Get group: ', nc.get_groups())
#
#     print('Get user group: ', nc.get_user_groups(user_name='admin'))
#     print('Get user group: ', nc.get_user_groups(user_name='user1'))
#
#     print('Get member of group: ', nc.get_group_members(group_name='admin'))
#
#     group_name_new = 'MTS_' + random_str()
#     print('Create group: ', nc.create_group(group_name=group_name_new))
#     print('Get group exist: ', nc.group_exists(group_name=group_name_new))
#
#     print('Set password: ', nc.set_user_attribute(user_name='user1', key='password', value='111111AbC*'))
#     user_put_file(group_name=group_name_new)
#
#
# normal_display_func()
