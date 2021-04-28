#!/usr/bin/python3
import sys
import socket
import asyncio
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
    
    @staticmethod
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
        return t

    def showTransferRate(self):
        rate = "%.3f" % self.calcTransferRate(self.testOutput)
        sys.stdout.write('\b' * 6)
        sys.stdout.write("Transfer Rate: " + rate)
        sys.stdout.flush()

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

            print(result)
            queue.task_done()
    
    @staticmethod
    def makeTransferQueue(source, destination, numTransfers):
        queue = asyncio.Queue()
        for num in range(numTransfers):
            cmd = ['curl', '-L', '-X', 'COPY']
            cmd += ['-H', 'Overwrite: T']
            cmd += ['-H', f'Source: http://{source}:1094/testFile']
            cmd += [f'http://{destination}:1094/testDestFile{num}']
            queue.put_nowait(cmd)
        return queue

    async def runTransfers(self):
        self.checkSocket(self.source, self.destination)
        
        logging.debug("Building queue with " + str(self.numTransfers) + " transfers")
        queue = self.makeTransferQueue(self.source, self.destination, self.numTransfers)
        logging.debug("Queue built successfully")

        logging.info("\nSTARTING TRANSFERS\n")
        
        tasks = []
        for i in range(self.numTransfers):
            task = asyncio.create_task(self.worker(f'worker-{i}', queue, self.testOutput))
            showTransferRate()
            tasks.append(task)
        
        await queue.join()
        
        for task in tasks:
            task.cancel()

if __name__ == "__main__":
    logging.basicConfig(filename='transfer.log', filemode='w', level=logging.INFO, format='%(asctime)s  %(levelname)s - %(message)s', datefmt='%Y%m%d %H:%M:%S')
    source, destination, numTransfers = sys.argv[1:4]
    t = TransferTest(source, destination, numTransfers)
    asyncio.run(t.runTransfers())