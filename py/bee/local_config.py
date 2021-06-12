import pathlib
import json
import os

store_path=os.getenv("BEE_STORE_PATH")

if store_path == None:
  "/opt/data"

def config_path_by_index(config_path_index):
  return f"{store_path}/{config_path_index}"
  # return f"/Users/peanut/wcx_workspace/tmp-data/{config_path_index}"

# 初始化的配置文件
def config_file_by_index(config_path_index) -> pathlib.Path:
  return pathlib.Path(f"{config_path_by_index(config_path_index)}/node_info.json")

# bee的datadir
def data_path_by_index(config_path_index):
  return f"{config_path_by_index(config_path_index)}/bee-data"

def save_local_config(config_path_index, config):
  old_config = load_local_config(config_path_index)
  if old_config == None:
    old_config = {}
  for k in config:
    old_config[k] = config[k]
  
  json_content = json.dumps(old_config)
  config_file = config_file_by_index(config_path_index)
  with open(config_file, 'w') as f:
    f.write(json_content)

def load_local_config(config_path_index):
  config_file = config_file_by_index(config_path_index)
  if not config_file.exists():
    return None
  if not config_file.is_file():
    raise ValueError("node_info.json 不是一个文件")
  config = None
  with open(config_file, 'r') as f:
    content = f.read()
    config =json.loads(content)
  return config
