

import websockets

from websockets.exceptions import ConnectionClosed
from py.message.ws_protocol import WSCommand, WSMessage
from py.bee.bee_holder import BeeHolder
from py.bee.ws_handle import reconnect_if_needed, perform_handshake, start_ping_task, handle_message_receive, receive_message, send_message



async def connect(bee: BeeHolder, ws_url: str):
  connection = await websockets.connect(ws_url)
  
  await perform_handshake(connection)

  bee.start()

  await start_ping_task(connection)

  while bee.isRunning():
    try:
      (connection, tried) = await reconnect_if_needed(connection, bee, ws_url)
      if connection == None:
        break
      if tried:
        await start_ping_task(connection)
      
      message = await receive_message(connection)
      
      if message != None and message.command == WSCommand.pong:
        pass
      elif message != None:
        await handle_message_receive(connection, message)
    except ConnectionClosed as err:
      # err.reason
      print(f'closed by forgein code={err.code}, reason={err.reason}')
      if err.code == 1003:
        # nodeId 或者 localSerialNumber 错误
        break

  print('exit')
  if bee is not None and bee.isRunning():
    bee.shutdown()
  if connection != None and not connection.closed:
    await connection.close()
  exit()
    
