# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 14:28:25 2021

@author: pranay
"""


# create cryptocurrency 
# FLASK==0.12.2 : pip install Flask == 0.12.2
# Postman HTTP client : https://www.getpostman.com
# requests==2.18.4 : pip install  

# for simplicity
# the proof-of-work does not include the whole block hash but a function of only previous hash
# merkel root is not included
# incoming transactions are stored in the the blockchain itself rather than mempool storage
import datetime
import hashlib
import json
from flask import Flask , jsonify , request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Building blockchain

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1 , previous_hash = '0')
        self.nodes = set()
        
    def create_block(self, proof , previous_hash):
        block = {'index' : len(self.chain) + 1 ,
                 'timestamp' : str(datetime.datetime.now()) ,
                 'proof' : proof,
                 'previous_hash' : previous_hash,
                 'transactions' : self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self , previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self , block):
        encoded_block = json.dumps(block , sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self,chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            # chech nonce validity
            prev_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - prev_proof).encode()).hexdigest()
            # check for the leading zeros
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
            
        return True
    
    def add_transaction(self,sender , receiver , amount):
        self.transactions.append({'sender':sender ,
                                  'receiver':receiver , 
                                  'amount' : amount})
        previous_block = self.get_previous_block()
        return previous_block['index']+1
    
    # adding the nodes in the node set
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    # replace if bigger chain is present
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        # max_lenght shows the maximum lenght till now
        max_lenght = len(self.chain)
        
        # send request to get lenght in other chains
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_lenght and is_chain_valid(chain) :
                    longest_chain = chain
                    max_lenght = length
        
        if longest_chain:
            self.chain = longest_chain
            return True
        
        return False
        


# PART2 - Mining your blockchain

# creating the webapp
app = Flask(__name__)

#creating address to receive crypto ( like mining fees ) on port 5000
node_address = str(uuid4()).replace('-','')



# creating a blockchain
blockchain = Blockchain()



@app.route('/mine_block' , methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address , receiver = 'Brijesh' , amount = 20)
    block = blockchain.create_block(proof, previous_hash)
    
    respose = {'message' : 'Congratualations for mining the block',
               'index' : block['index'],
               'timestamp' : block['timestamp'],
               'proof' : block['proof'],
               'previous_hash' : block['previous_hash'],
               'transactions' : block['transactions']}
    
    return jsonify(respose) , 200

# getting the full blockchain
@app.route('/get_chain' , methods=['GET'])
def get_chain():
    response = {'chain' : blockchain.chain,
                'length' : len(blockchain.chain)}
    
    return jsonify(response) , 200

# checking if blockchain is valid
@app.route('/is_valid' , methods = ['GET'])
def is_valid():
    response = {'valid' : blockchain.is_chain_valid(blockchain.chain)}
    
    return jsonify(response) , 200

# adding new transactions in blockchain
@app.route('/add_transaction' , methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender' , 'receiver' , 'amount']
    
    # check for invalid transaction format
    if not all (key in response for key in transaction_keys):
        return 'Missing elements' , 400
    
    index = blockchain.add_transaction(json['sender'], json['receiver'],json['amount'])
    response = {'message': f'transaction added at block no {index}'}
    
    return jsonify(response), 201

@app.route('/change_illegal' , methods = ['GET'])
def change_illegal():
    blockchain.chain[1]['previous_hash'] = blockchain.chain[2]['previous_hash']
    response = {'key' : blockchain.chain[1]['index']}
    
    return jsonify(response),200



# PART 3 -- Decentralization of the blockchain

# connecting new nodes (for simplicity the nodes are added at once)
@app.route('/connect_node',methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    
    if nodes is None:
        return "No node" , 400
    
    for node in nodes:
        blockchain.add_node(node)
    
    response = {'message' : 'The nodes were added' ,
                'total_nodes': list(blockchain.nodes)}
    
    return jsonify(response) , 201


# replacing the chain with longest chain
@app.route('/replace_chain' , methods = ['GET'])
def replace_chain():
    change = blockchain.replace_chain()
    
    if change:
        response = {'message' : 'chain replaced by largest chain',
                    'new_chain' : blockchain.chain}
    else:
        response = {'message' : 'this chain is longest the longest',
                    'new_chain' : blockchain.chain}
    
    return jsonify(response) , 200


# running the app
app.run(host= '0.0.0.0' , port = 5002)


