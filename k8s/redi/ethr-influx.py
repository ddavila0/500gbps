import subprocess
import requests
import json

def runCmd(cmd):
  process = subprocess.Popen(cmd,
  shell=True, 
  stdout=subprocess.PIPE, 
  stderr=subprocess.PIPE)

  stdout, stderr = process.communicate()
  return stdout

if __name__ == '__main__':
  conf = json.loads(open('influx.conf','r').read())
  database = conf['database']
  username = conf['username']
  password = conf['password']

  url_string = f'http://graph.t2.ucsd.edu:8086/write?db={database}'
  throughput = runCmd('/home/ethr -c localhost -d 1s | grep \'TCP\' | sed \'s/^.*\(.\{8\}\)/\\1/\' | xargs')

  source = os.getenv('POD_IP')
  destination = os.getenv('DEST_POD_IP')

  data = f'source={source},destination={destination} value={throughput}'

  try:
    r = requests.post(url_string, auth=(username, password), data=data, timeout=40)
  except:
    print('error posting data')

