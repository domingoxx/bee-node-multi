import json
from py.bee.utils import gen_local_serial_number
from py.bee.local_config import config_path_by_index, data_path_by_index, save_local_config
import requests
import os

import urllib.request
import zipfile


admin_api_url = os.getenv("BEE_ADMIN_BASE_API")

if admin_api_url == None:
  raise ValueError("admin_api_url 不能为空")


def bind_and_init_config(secure_key, config_path_index, machine_name, machine_group, bee_version):
  local_serial_number = gen_local_serial_number(config_path_index)
  data = {
    'machineName': machine_name,
    'machineGroup': machine_group,
    'localSerialNumber': local_serial_number,
    'beeVersion': bee_version,
    'secureKey': secure_key,
  }
  response = requests.get(url=f"{admin_api_url}/api/bee/node/bind",json=data)
  json_data = response.json()
  
  success = json_data.get("success")
  if success == None or not success:
    raise ValueError(f"请求失败, result={json_data}")
  result = json_data['result']
  print(result)
  node_id = result['nodeId']
  deploy_zip_file_url = result['deployZipFileUrl']
  password = result['password']
  append_args = result['appendArgs']
  ws_url = result['wsUrl']
  boot_config_url = result['bootConfigUrl']

  data_path = data_path_by_index(config_path_index)

  extract_deploy_zip_file(deploy_zip_file_url, data_path)

  config = {
    'node_id': node_id,
    'local_serial_number': local_serial_number,
    'boot_config_url': boot_config_url,

    'append_args': append_args,
    'password': password,
    'ws_url': ws_url,
  }

  save_local_config(config_path_index, {
    'node_id': node_id,
    'local_serial_number': local_serial_number,
    'boot_config_url': boot_config_url,
  })

  return config


def extract_deploy_zip_file( url, data_path):
  file_name, headers = urllib.request.urlretrieve(url)
  
  zf = zipfile.ZipFile(file_name, 'r')
  is_contain_keys_path = False
  is_contain_statestore_path = False
  for n in zf.namelist():
    if n == 'keys/':
      is_contain_keys_path = True
    if n == 'statestore/':
      is_contain_statestore_path = True

    if is_contain_keys_path and is_contain_statestore_path:
      break
  if is_contain_keys_path and is_contain_statestore_path:
    for n in zf.namelist():
      if n.startswith('keys') or n.startswith('statestore'):
        zf.extract(n, data_path)
  else:
    raise ValueError(f"zip包格式不正确， 缺少keys={not is_contain_keys_path},缺少statestore={not is_contain_statestore_path}")
  zf.close()


def request_boot_config(local_config, machine_group, machine_name, bee_version):
  url = local_config['boot_config_url']
  params = {
    'nodeId': local_config['node_id'],
    'localSerialNumber': local_config['local_serial_number'],
     'machineGroup': machine_group, 
     'machineName': machine_name, 
     'beeVersion': bee_version
  }
  response = requests.get(url=url, params=params)
  json_data = response.json()
  success = json_data.get("success")
  if success == None or not success:
    raise ValueError(f"请求失败, result={json_data}")
  result = json_data['result']
  
  local_config['append_args'] = result['appendArgs']
  local_config['password'] = result['password']
  local_config['ws_url'] = result['wsUrl']

  return local_config
