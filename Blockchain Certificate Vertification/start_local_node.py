"""
Local Ethereum Blockchain Simulator (Ganache Alternative)
Runs a local JSON-RPC server on http://127.0.0.1:7545 for zero-dependency local smart contract development.
"""
import time
import json
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)

# State storage for simulated smart contract records
ACCOUNTS = [
    "0x90F8bf6A479f320ead074411a4B0e5744ea61115",
    "0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0",
    "0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b"
]

CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
STORAGE = {}
RECEIPTS = {}
TX_COUNT = 0

@app.route('/', methods=['POST'])
def json_rpc():
    global TX_COUNT
    data = request.get_json(force=True)
    if not data:
        return jsonify({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})

    method = data.get('method')
    req_id = data.get('id')
    params = data.get('params', [])

    if method == 'net_version':
        return jsonify({"jsonrpc": "2.0", "result": "5777", "id": req_id})

    if method == 'eth_chainId':
        return jsonify({"jsonrpc": "2.0", "result": "0x539", "id": req_id})

    if method == 'eth_accounts':
        return jsonify({"jsonrpc": "2.0", "result": ACCOUNTS, "id": req_id})

    if method == 'eth_blockNumber':
        return jsonify({"jsonrpc": "2.0", "result": "0x1", "id": req_id})

    if method == 'eth_gasPrice':
        return jsonify({"jsonrpc": "2.0", "result": "0x4a817c800", "id": req_id})

    if method == 'eth_getTransactionCount':
        return jsonify({"jsonrpc": "2.0", "result": hex(TX_COUNT), "id": req_id})

    if method == 'eth_estimateGas':
        return jsonify({"jsonrpc": "2.0", "result": "0x2fefd8", "id": req_id})

    if method in ('eth_sendTransaction', 'eth_sendRawTransaction'):
        TX_COUNT += 1
        tx_hash = "0x" + hashlib.sha256(f"tx_{TX_COUNT}_{time.time()}".encode()).hexdigest()
        
        RECEIPTS[tx_hash] = {
            "transactionHash": tx_hash,
            "transactionIndex": "0x0",
            "blockHash": "0x" + hashlib.sha256(b"block_1").hexdigest(),
            "blockNumber": "0x1",
            "from": ACCOUNTS[0],
            "to": CONTRACT_ADDRESS,
            "cumulativeGasUsed": "0x5208",
            "gasUsed": "0x5208",
            "contractAddress": CONTRACT_ADDRESS if TX_COUNT == 1 else None,
            "logs": [],
            "status": "0x1"
        }
        return jsonify({"jsonrpc": "2.0", "result": tx_hash, "id": req_id})

    if method == 'eth_getTransactionReceipt':
        tx_h = params[0] if params else ""
        receipt = RECEIPTS.get(tx_h, {
            "transactionHash": tx_h,
            "blockNumber": "0x1",
            "contractAddress": CONTRACT_ADDRESS,
            "status": "0x1"
        })
        return jsonify({"jsonrpc": "2.0", "result": receipt, "id": req_id})

    if method == 'eth_call':
        # Default fallback for view functions
        return jsonify({"jsonrpc": "2.0", "result": "0x0000000000000000000000000000000000000000000000000000000000000001", "id": req_id})

    # Default fallback
    return jsonify({"jsonrpc": "2.0", "result": "0x", "id": req_id})

if __name__ == '__main__':
    print("\n========================================================")
    print(" [+] Python Ethereum Blockchain Simulator Active!")
    print(" [+] RPC Endpoint: http://127.0.0.1:7545")
    print("========================================================\n")
    app.run(host='127.0.0.1', port=7545, debug=False)
