import threading, subprocess, signal, os


def kill_child_processes(parent_pid, sig=signal.SIGTERM):
  ps_command = subprocess.Popen("ps -o pid --ppid %d --noheaders" % parent_pid, shell=True, stdout=subprocess.PIPE)
  ps_output = ps_command.stdout.read()
  ps_output = str(ps_output, encoding="utf-8")
  retcode = ps_command.wait()
  assert retcode == 0, "ps command returned %d" % retcode
  for pid_str in ps_output.split("\n")[:-1]:
    os.kill(int(pid_str), sig)





class BeeHolder(threading.Thread):
  def __init__(self,password, datadir, append_args):
    threading.Thread.__init__(self)
    self.datadir = datadir
    self.password = password
    self.append_args = append_args
    self.bee_process = None
    self.running = False

  def start(self) -> None:
    self.running = True
    return super().start()

  def run(self):
    # self.bee_process = 1
    # time.sleep(600)
    # self.bee_process = None
    self.startBee()
    self.running = False

  def isRunning(self):
    return self.running
    # return self.bee_process != None and self.bee_process.returncode == None
    # return self.bee_process != None

  def shutdown(self):
    if self.bee_process.returncode == None:
      print('send terminate bee', flush=True)
      kill_child_processes(self.bee_process.pid)
      self.bee_process.terminate()
      self.bee_process.wait(5)
      if self.bee_process.returncode == None:
        print(f'send kill bee {self.bee_process.pid}', flush=True)
        subprocess.check_output(f"kill -9 {self.bee_process.pid}", shell=True)

  def startBee(self):
    
    print('开始启动')
    
    # --clef-signer-enable  --clef-signer-endpoint http://127.0.0.1:8551

    cmd = f"""
      bee start {self.append_args} --password {self.password} --data-dir {self.datadir} 
    """
    print(cmd)
    self.bee_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE)
    
    while self.bee_process.returncode == None:
      result = self.bee_process.stdout.readline()
      logStr = str(result[:-1], encoding="utf-8")
      print(logStr, flush=True)
      if logStr.find("using ethereum address") != -1:
        splitList = logStr.split("using ethereum address")
        address = splitList[1][1:-2]
        print(address)
        
        
      self.bee_process.poll()
    
    print('Bee退出',flush=True)
