import subprocess
import os
import string
import random

def get_api_secure_key():
  envVar = os.getenv("BEE_API_SECURE_KEY")
  if envVar == None:
    raise ValueError("无法获取 secure key")
  return envVar

def get_bee_version():
  version_data = os.getenv("BEE_VERSION")
  if version_data == None:
    version_data = subprocess.check_output('bee  version', shell=True)
    version = str(version_data, encoding='utf-8').split("-")[0].split(".")
  else:
    version = version_data.split(".")
  try:
    for v in version:
      int(v)
  except:
    raise ValueError(f"{version_data} 不能转为版本号")

  return ".".join(version)

def gen_local_serial_number(config_path_index):
  random_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
  return f"{config_path_index}-bee-{random_str}"

def get_config_path_index():
  envVar = os.getenv("BEE_CONFIG_PATH_INDEX")
  if envVar != None:
    return int(envVar)
  container_name = subprocess.check_output('dig -x "$(hostname -i)" +short | cut -f1 -d .', shell=True)

  config_path_index = str(container_name[:-1], encoding='utf-8')
  config_path_index = int(config_path_index.split("_")[-1:][0])
  if config_path_index >= 100 or config_path_index <= 0:
    raise ValueError('config_path_index value must be 1 ~ 99')

  return config_path_index

def get_machine_name():
  envVar = os.getenv("BEE_MACHINE_NAME")
  if envVar != None:
    return envVar
  hostname = subprocess.check_output('cat /opt/hostname', shell=True)
  return str(hostname[:-1], encoding='utf-8')

def get_machine_group():
  envVar = os.getenv("BEE_MACHINE_GROUP")
  if envVar != None:
    return envVar
  machine_name = get_machine_name()
  name_arr = machine_name.split("-")
  if len(name_arr) <= 1:
    raise ValueError(f"无法从{machine_name}截取group")
  return name_arr[0].upper()

def load_content_from_file(filepath: str):
  with open(filepath) as file:
    return file.read().replace("\n","")