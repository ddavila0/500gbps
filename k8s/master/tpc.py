import sys
import socket
import asyncio
import threading
import logging

def calcTransferRate(output):
  throughput = list()
  for item in output:
    timeStamps = list()
    transferStripes = list()
    tmpThroughput = 0
    for line in item.split('\n'):
      if "Timestamp" in line:
        timeStamps.append(line.split()[1])
      elif "Stripe Bytes Transferred" in line:
        transferStripes.append(line.split()[3])
    for i in range(len(timeStamps)-1):
      tmpThroughput += (float(transferStripes[i+1]) - float(transferStripes[i])) / (float(timeStamps[i+1]) - float(timeStamps[i]))
    try:
      throughput.append(tmpThroughput / (len(timeStamps)-1))
    except:
      logging.error("Transfers are too fast")
  t = sum(throughput) / 134217728
  print(t,end='\r')

def checkSocket(source, destination):
  source_sock = socket.socket()
  dest_sock = socket.socket()
  try:
    source_sock.connect((source, 1094))
    dest_sock.connect((destination, 1094))
    logging.info("Succesfully contacted socket 1094 on both sides")
  except Exception as e:
    source_sock.close()
    dest_sock.close()
    logging.error("Error while connecting to socket")
    sys.exit(1)
  finally:
    source_sock.close()
    dest_sock.close()

class TransferTest:
  def __init__(self, source, destination, numTransferStart, numTransferEnd):
    self.source = source
    self.destination = destination
    self.numTransferStart = int(numTransferStart)
    self.numTransferEnd = int(numTransferEnd)
    self.testOutput = list()
  
  @staticmethod
  async def worker(name, queue, output):
    while True:
      cmd = await queue.get()

      process = await asyncio.create_subprocess_exec(
      *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

      stdout, stderr = await process.communicate()
      result = stdout.decode().strip()
      output.append(result)
      queue.put_nowait(cmd)

      queue.task_done()

  def makeTransferQueue(self):
    queue = asyncio.Queue()
    for num in range(self.numTransferStart, self.numTransferEnd):
      cmd = ['curl', '-L', '-X', 'COPY']
      cmd += ['-H', 'Overwrite: T']
      cmd += ['-H', f'Source: https://{self.source}:1094/testSourceFile{num}']
      cmd += [f'https://{self.destination}:1094/testDestFile{num}']
      cmd += ['--capath', '/etc/grid-security/certificates/']
      queue.put_nowait(cmd)
    return queue

  async def runTransfers(self):
    checkSocket(self.source, self.destination)

    logging.info("Building queue...")
    queue = self.makeTransferQueue()
    logging.info("Queue built successfully")
    logging.info("STARTING TRANSFERS...")

    tasks = []
    for i in range((self.numTransferEnd - self.numTransferStart)):
      task = asyncio.create_task(self.worker(f'worker-{i}', queue, self.testOutput))
      tasks.append(task)

    await queue.join()

    for task in tasks:
      task.cancel()

  def startTransfers(self):
    asyncio.run(self.runTransfers())

def main():
  logging.basicConfig(filename='transfer.log', filemode='w', level=logging.INFO, format='%(asctime)s  %(levelname)s - %(message)s', datefmt='%Y%m%d %H:%M:%S')

  source, destination, numTransfers, numServers = sys.argv[1:5]
  transferList = []
  NUM_THREADS = int(numServers)
  
  totalTransfers = int(numTransfers) * int(numServers)
  doTransfer = lambda i : TransferTest(source, destination, i, i + totalTransfers / NUM_THREADS).startTransfers()
  
  threads = [ threading.Thread(target = doTransfer, args=(i,)) for i in range(0, totalTransfers, totalTransfers // NUM_THREADS) ]
  [ t.start() for t in threads ]
  [ t.join() for t in threads ]

if __name__ == "__main__":
  main()
