import sys
import socket
import asyncio
import threading
import logging

class TransferTest:
  def __init__(self, source, destination, numTransferStart, numTransferEnd):
    self.source = source
    self.destination = destination
    self.numTransferStart = int(numTransferStart)
    self.numTransferEnd = int(numTransferEnd)

  @staticmethod
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

  @staticmethod
  async def worker(name, queue):
    while True:
      cmd = await queue.get()

      process = await asyncio.create_subprocess_exec(
      *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

      stdout, stderr = await process.communicate()
      result = stdout.decode().strip()
      queue.put_nowait(cmd)
      print(result)
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
    self.checkSocket(self.source, self.destination)

    logging.info("Building queue...")
    queue = self.makeTransferQueue()
    logging.info("Queue built successfully")
    logging.info("STARTING TRANSFERS...")

    tasks = []
    for i in range(2 * (self.numTransferEnd - self.numTransferStart)):
      task = asyncio.create_task(self.worker(f'worker-{i}', queue))
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
  NUM_THREADS = int(numServers) // 2
  
  totalTransfers = int(numTransfers) * int(numServers)
  doTransfer = lambda i : TransferTest(source, destination, i, i + totalTransfers // NUM_THREADS).startTransfers()
  
  threads = [ threading.Thread(target = doTransfer, args=(i,)) for i in range(0, totalTransfers, totalTransfers // NUM_THREADS) ]
  [ t.start() for t in threads ]
  [ t.join() for t in threads ]

if __name__ == "__main__":
  main()
