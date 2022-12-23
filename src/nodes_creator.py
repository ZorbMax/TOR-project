import time
import threading
from src import node

port = 50001
threadList = []

"""
Responsable for instanciate the threads of local nodes for the p2p network
"""
while True:
    threadListTemp = []
    nodes = input('Number of nodes you want to add : ')
    for i in range(int(nodes)):
        threadListTemp.append(threading.Thread(target=node.newNode, args=(port,)))
        port += 1
    for thread in threadListTemp:
        thread.start()
    threadList += threadListTemp
    time.sleep(1)