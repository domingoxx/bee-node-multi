

class WSCommand:
  handshake_hi='handshake_hi'
  ping = 'ping'
  pong = 'pong'
  http_call = 'http_call'
  http_return = 'http_return'


class WSMessage:
  def __init__(self, command: str, data: any = None) -> None:
    
    self.command = command
    self.data = data
      

  def strData(self) -> str:
    return self.data
  
  def dictData(self) -> dict:
    return self.data


