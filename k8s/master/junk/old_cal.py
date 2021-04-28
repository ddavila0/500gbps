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
        """ Check both source and destination side for port 1094.
            Exit if closed.
        """
        source_sock = socket.socket()
        dest_sock = socket.socket()
        try:
            source_sock.connect((source, 1094))
            dest_sock.connect((destination, 1094))
            logging.debug("Connected to Socket 1094 on both Server Sides")
        except Exception as e:
            source_sock.close()
            dest_sock.close()
            sys.exit(1)
            logging.error("Error while connecting to socket")
        finally:
            source_sock.close()
            dest_sock.close()
    
    @staticmethod
    async def runCmd(*cmd):
        """ Run async cmd in shell
        """
        process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        
        stdout, stderr = await process.communicate()
        result = stdout.decode().strip()
        return result
    
    def makeTransferCmd(self):
        for num in range(self.numTransfers):
            cmd = ['curl', '-L', '-X', 'COPY']
            cmd += ['-H', 'Overwrite: T']
            cmd += ['-H', f'Source: http://{self.source}:1094/testFile']
            cmd += [f'http://{self.destination}:1094/testDestFile{num}']
            logging.info("Ran Command: " + str(cmd))
            yield self.runCmd(cmd)

    # TODO: Live calcRate
    @staticmethod
    def calcRate(output):
        throughput = list()
        for item in output.testOutput:
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
            throughput.append(tmpThroughput) / (len(timeStamps)-1))
        t = sum(throughput) / 134217728
        print(t)

    def runTransfers(self):
        self.checkSocket(self.source, self.destination)
        transfer = self.makeTransferCmd() 
        """ Run transfers until interrupted
        """
        if asyncio.get_event_loop().is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        logging.info("\nSTARTING TRANSFERS\n\n")
        while True:
            for i in range(self.numTransfers):
                results = loop.run_until_complete(next(transfer))
                self.testOutput.append(results)

            self.calcRate(self)

        loop.close()

if __name__ == "__main__":
    logging.basicConfig(filename='transfer.log', filemode='w', level=logging.INFO, format='%(asctime)s  %(levelname)s - %(message)s', datefmt='%Y%m%d %H:%M:%S')
    source, destination, numTransfers = sys.argv[1:4]
    t = TransferTest(source, destination, numTransfers)
    t.runTransfers()
