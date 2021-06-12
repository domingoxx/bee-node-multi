import asyncio
import json
import requests
from websockets import WebSocketClientProtocol
import websockets
from websockets.exceptions import ConnectionClosed
from py.message.ws_protocol import WSMessage, WSCommand
from py.bee.bee_holder import BeeHolder

async def receive_message(ws: WebSocketClientProtocol):
  message =  await ws.recv()
  if message == None:
    return None
  
  json_data = json.loads(message)
  
  return WSMessage(json_data['command'], json_data.get('data'))

async def send_message(ws: WebSocketClientProtocol, message: WSMessage):
  assert message != None
  json_str = json.dumps(message.__dict__, ensure_ascii=False)
  await ws.send(json_str)


async def perform_handshake(ws: WebSocketClientProtocol):

  await send_message(ws, WSMessage(WSCommand.handshake_hi))
  message = await receive_message(ws)
  print(message)
  if message != None and message.command == WSCommand.handshake_hi:
    return True

  return False


async def reconnect_if_needed(ws: WebSocketClientProtocol, bee: BeeHolder, url: str):
  if not ws.closed:
    return ws, False
  if not bee.isRunning():
    return None, False

  # 开始重连
  while bee.isRunning():
    try:
      print('重连中...', flush=True)
      connection = await websockets.connect(url)
      success = await perform_handshake(connection)
      if success:
        print('重连成功', flush=True)
        return connection, True
      else:
        await connection.close()
        print('重连失败！', flush=True)
    except ConnectionClosed as cc:
      # 被服务器主动断开
      if cc.code == 1003:
        return None, False
    except BaseException as err:
      print('重连失败～',err, flush=True)
    
    await asyncio.sleep(10)
  return None, False

async def start_ping_task(ws: WebSocketClientProtocol):
  loop = asyncio.get_event_loop()

  async def task():
    while not ws.closed:
      await send_message(ws,WSMessage(WSCommand.ping))
      await asyncio.sleep(60)
  loop.create_task(task())




async def handle_http_call_message(ws: WebSocketClientProtocol, message: WSMessage):
  data = message.dictData()
  print('handle http call', data, flush=True)
  message_response = {'key': data['key']}
  try:
    response = requests.request(
      method=data['method'],
      url=data['url'],
      params=data.get('params'),
      headers=data('headers'),
      json=data.get('json')
      )

    json_data = response.json()
    script = data.get('eval')
    
    if script != None:
      print(json_data, flush=True)
      json_data = eval(script, {'res': json_data})
    message_response['success'] = True
    message_response['result'] = json_data
  except BaseException as err:
    message_response['success'] = False
    message_response['result'] = str(err)
  
  await send_message(ws, WSMessage(WSCommand.http_return, message_response))




handle_map = {
  WSCommand.http_call: handle_http_call_message
}

async def handle_message_receive(ws: WebSocketClientProtocol, message: WSMessage):
  handle = handle_map.get(message.command)
  if handle != None:
    await handle(ws, message)