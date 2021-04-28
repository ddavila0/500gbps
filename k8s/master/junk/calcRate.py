#!/usr/bin/python3
import sys
import subprocess
import socket
import asyncio
from datetime import datetime
import logging

class TransferTest:
    def __init__(self, source, destination, numTransfers):
        self.source = source
        self.destination = destination
        self.numTransfers = int(numTransfers)
        self.testOutput = list()
    
    @staticmethod 
    def checkSocket(source, destination):
        source_sock = socket.socket()
        dest_sock = socket.socket()
        try:
            source_sock.connect((source, 1094))
            dest_sock.connect((destination, 1094))
            logging.debug("Succesfully contacted socket 1094 on both sides")
        except Exception as e:
            source_sock.close()
            dest_sock.close()
            logging.error("Error while connecting to socket")
            sys.exit(1)
        finally:
            source_sock.close()
            dest_sock.close()
    
    # TODO: Live calcRate
    @staticmethod
    def calcRate(numTransfers, output):
        throughput = list()
        for item in output[-numTransfers:-1]:
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
                throughput.append(tmpThroughput) / (len(timeStamps)-1))
            except:
                logging.error("Transfers are too fast")
        t = sum(throughput) / 134217728
        print(t) 
    
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

    def makeTransferCmd(self):
        for num in range(self.numTransfers):
            cmd = ['curl', '-L', '-X', 'COPY']
            cmd += ['-H', 'Overwrite: T']
            cmd += ['-H', f'Source: http://{self.source}:1094/testFile']
            cmd += [f'http://{self.destination}:1094/testDestFile{num}']
            logging.info("Ran Command: " + str(cmd))
            yield cmd

    async def runTransfers(self):
        self.checkSocket(self.source, self.destination)
        queue = asyncio.Queue()
        transfer = self.makeTransferCmd() 
        logging.info("\nSTARTING TRANSFERS\n\n")
        
        for i in range(self.numTransfers):
            queue.put_nowait(next(transfer))

        tasks = []
        for i in range(self.numTransfers):
            task = asyncio.create_task(self.worker(f'worker-{i}', queue, self.testOutput)) 
            try:
                self.calcRate(self.numTransfers, self.testOutput)
            except:
                pass
            tasks.append(task)
        
        await queue.join()
        
        for task in tasks:
            task.cancel()

if __name__ == "__main__":
    logging.basicConfig(filename='transfer.log', filemode='w', level=logging.INFO, format='%(asctime)s  %(levelname)s - %(message)s', datefmt='%Y%m%d %H:%M:%S')
    source, destination, numTransfers = sys.argv[1:4]
    t = TransferTest(source, destination, numTransfers)
    t.runTransfers()
