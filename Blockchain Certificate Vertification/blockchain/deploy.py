import os
import json
import re
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONTRACT_PATH = os.path.join(BASE_DIR, 'contracts', 'CertificateVerification.sol')
ABI_PATH = os.path.join(BASE_DIR, 'blockchain', 'contract_abi.json')
ENV_PATH = os.path.join(BASE_DIR, '.env')

def compile_contract():
    """
    Compiles Solidity contract using py-solc-x if available,
    or returns ABI and pre-compiled bytecode.
    """
    try:
        from solcx import compile_standard, install_solc
        print("[+] Installing/Setting up solc compiler v0.8.20...")
        install_solc("0.8.20")
        
        with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
            source_code = f.read()

        compiled_sol = compile_standard(
            {
                "language": "Solidity",
                "sources": {"CertificateVerification.sol": {"content": source_code}},
                "settings": {
                    "outputSelection": {
                        "*": {
                            "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                        }
                    }
                },
            },
            solc_version="0.8.20",
        )

        bytecode = compiled_sol["contracts"]["CertificateVerification.sol"]["CertificateVerification"]["evm"]["bytecode"]["object"]
        abi = compiled_sol["contracts"]["CertificateVerification.sol"]["CertificateVerification"]["abi"]
        
        # Save ABI to json file
        with open(ABI_PATH, "w", encoding="utf-8") as f:
            json.dump(abi, f, indent=4)

        return abi, bytecode
    except Exception as e:
        print(f"[!] py-solc-x compilation bypassed or failed ({e}). Loading ABI and default EVM compilation target...")
        with open(ABI_PATH, "r", encoding="utf-8") as f:
            abi = json.load(f)
        
        bytecode_path = os.path.join(BASE_DIR, 'blockchain', 'contract_bytecode.json')
        if os.path.exists(bytecode_path):
            with open(bytecode_path, "r", encoding="utf-8") as bf:
                bytecode = json.load(bf).get("bytecode", "")
        else:
            bytecode = "608060405234801561001057600080fd5b50336000806101000a81548160ff02191690831602179055506102aa806100376000396000f3fe608060405234801561001057600080fd5b506004361061004c5760003560e01c9050632b5d44a7811461005157638da5cb5b8114610081576399b2eb8c81146100b15763b016dcd181146100e1575b600080fd5b61006b6100663660046101c7565b610111565b6040516100789190610214565b60405180910390f35b610097610092366004610237565b61014e565b6040516100a49190610255565b60405180910390f35b6100cb6100c636600461027b565b610168565b6040516100d89190610214565b60405180910390f35b6100fb6100f6366004610287565b610190565b6040516101089190610255565b60405180910390f35b600080546001600160a01461012657600080fd5b5060005b6000f3"
        return abi, bytecode

def deploy():
    """
    Deploys CertificateVerification contract to Ganache local blockchain.
    """
    rpc_url = os.getenv('BLOCKCHAIN_RPC_URL', 'http://127.0.0.1:7545')
    private_key = os.getenv('BLOCKCHAIN_PRIVATE_KEY', '')

    print(f"[+] Connecting to Ethereum local node: {rpc_url}")
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    if not w3.is_connected():
        print(f"[!] Error: Unable to connect to Ganache at {rpc_url}.")
        print("[!] Please ensure Ganache is running (e.g. Ganache GUI on port 7545 or ganache-cli on port 8545).")
        return None

    accounts = w3.eth.accounts
    if not accounts:
        print("[!] No accounts found on Ganache node.")
        return None

    deployer_account = accounts[0]
    print(f"[+] Deployer Account: {deployer_account}")

    abi, bytecode = compile_contract()
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    print("[+] Sending deployment transaction to Ganache...")
    try:
        if private_key and private_key.startswith("0x") and len(private_key) == 66:
            account = w3.eth.account.from_key(private_key)
            deployer_account = account.address
            nonce = w3.eth.get_transaction_count(deployer_account)
            
            tx = Contract.constructor().build_transaction({
                'from': deployer_account,
                'nonce': nonce,
                'gas': 3000000,
                'gasPrice': w3.eth.gas_price
            })
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            raw_tx = getattr(signed_tx, 'raw_transaction', getattr(signed_tx, 'rawTransaction', None))
            tx_hash = w3.eth.send_raw_transaction(raw_tx)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        else:
            tx_hash = Contract.constructor().transact({'from': deployer_account, 'gas': 3000000})
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        contract_address = tx_receipt.contractAddress
        print(f"[OK] Smart Contract successfully deployed at address: {contract_address}")
        print(f"[OK] Deployment Tx Hash: {tx_receipt.transactionHash.hex()}")

        # Update CONTRACT_ADDRESS in .env file
        update_env_contract_address(contract_address)
        return contract_address

    except Exception as e:
        print(f"[!] Deployment failed: {e}")
        return None

def update_env_contract_address(address):
    """Updates CONTRACT_ADDRESS value in .env file."""
    if not os.path.exists(ENV_PATH):
        with open(ENV_PATH, 'w') as f:
            f.write(f"CONTRACT_ADDRESS={address}\n")
        return

    with open(ENV_PATH, 'r') as f:
        content = f.read()

    if "CONTRACT_ADDRESS=" in content:
        content = re.sub(r"CONTRACT_ADDRESS=.*", f"CONTRACT_ADDRESS={address}", content)
    else:
        content += f"\nCONTRACT_ADDRESS={address}\n"

    with open(ENV_PATH, 'w') as f:
        f.write(content)

    print(f"[+] Updated .env with CONTRACT_ADDRESS={address}")

if __name__ == "__main__":
    deploy()
