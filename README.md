# ELEC-H417 : TOR PROJECT

The goal of this project is to design and implement a TOR network that enables
anonymous usage of a network.

First, the cryptography library is used in this project, so you will need to install it using :
> pip install cryptography

The github contains 5 python files and 4 of them has to be running at the same time

1. directory_server.py
2. nodes_creator.py
3. client.py
4. challenger_response_server.py

First run the directory_server.py. It will be in charge to keep track of the nodes.

In the nodes_creator.py, the number of nodes will be asked and the number of nodes will connect to the directory server.
You can add more nodes at any time in the network.

client.py and challenger_response_server.py are here to use the p2p network to communicate. 
challenger_response_server.py will ask you to setup the password of the client. 
Then, you can try to authenticate on the client terminal using the password.
