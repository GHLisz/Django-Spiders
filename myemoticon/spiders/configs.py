import os

host_url = ''
database_name = ''
pic_root_folder = 'D:/sppic'

channel_blacklist = []

current_path = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(current_path, 'log', 'log.txt')
error_list_path = os.path.join(current_path, 'log', 'error_list.txt')

if not os.path.exists(os.path.join(current_path, 'log')):
    os.makedirs(os.path.join(current_path, 'log'))
