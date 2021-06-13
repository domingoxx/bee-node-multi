from py.bee.ws_connection import connect
from py.bee.bee_holder import BeeHolder
from py.bee.server_api import bind_and_init_config, request_boot_config
from py.bee.local_config import data_path_by_index, load_local_config
from py.bee.utils import get_bee_version, get_config_path_index, get_machine_group, get_machine_name, get_api_secure_key, load_content_from_file
from py.utils.register_exit import register_exit_fun
import asyncio

# 获取 localSerialNumber 



secure_key = get_api_secure_key()
bee_version = get_bee_version()
config_path_index = get_config_path_index()
machine_name = get_machine_name()
machine_group = get_machine_group()
data_path = data_path_by_index(config_path_index)
password = load_content_from_file(f"{data_path}/password.txt")
address = load_content_from_file(f"{data_path}/address.txt")
print(machine_group, machine_name, config_path_index, bee_version)


# 根据 config_path_index 检查文件是否存在
# 如果不存在，则请求绑定，并下载zip包解压
local_config = load_local_config(config_path_index)

if local_config == None:
  config = bind_and_init_config(secure_key, config_path_index, machine_name, machine_group, bee_version, address,password)
else:
  config = request_boot_config(local_config, machine_group, machine_name, bee_version)

config['password'] = password
config['secure_key'] = secure_key
config['machine_group'] = machine_group
config['machine_name'] = machine_name
config['config_path_index'] = config_path_index
config['bee_version'] = bee_version

print(config)
bee = BeeHolder(config['password'], data_path, config['append_args'])
register_exit_fun(bee.shutdown)

ws_url = f"{config['ws_url']}?localSerialNumber={config['local_serial_number']}"
print(ws_url)

asyncio.get_event_loop().run_until_complete(connect(bee, ws_url))

bee.shutdown()