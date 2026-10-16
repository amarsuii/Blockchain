import os
import json
import time
from web3 import Web3
from config import Config

class BlockchainService:
    def __init__(self, rpc_url=None, contract_address=None):
        self.rpc_url = rpc_url or Config.BLOCKCHAIN_RPC_URL
        self.contract_address = contract_address or Config.CONTRACT_ADDRESS
        self.w3 = None
        self.contract = None
        self._initialize_web3()

    def _initialize_web3(self):
        """Initializes Web3 provider and contract instance."""
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if not self.w3.is_connected():
                print(f"[!] Warning: Cannot connect to blockchain node at {self.rpc_url}")
                return

            abi_path = os.path.join(Config.BASE_DIR, 'blockchain', 'contract_abi.json')
            if os.path.exists(abi_path) and self.contract_address:
                with open(abi_path, 'r', encoding='utf-8') as f:
                    abi = json.load(f)
                
                # Check valid checksum address
                checksum_address = self.w3.to_checksum_address(self.contract_address)
                self.contract = self.w3.eth.contract(address=checksum_address, abi=abi)
        except Exception as e:
            print(f"[!] Blockchain initialisation error: {e}")

    def is_connected(self) -> bool:
        """Checks if Web3 node is accessible."""
        return self.w3 is not None and self.w3.is_connected()

    def register_certificate_on_chain(self, certificate_id: str, certificate_hash: str, issuer: str, timestamp: int = None) -> str:
        """
        Registers a certificate hash on the smart contract.
        Returns the blockchain transaction hash string.
        """
        if not self.is_connected():
            raise ConnectionError(f"Blockchain node unavailable at {self.rpc_url}. Please ensure Ganache is running.")

        if not self.contract:
            raise ValueError("Smart Contract address is not configured. Please run deploy_contract.py first.")

        if timestamp is None:
            timestamp = int(time.time())

        accounts = self.w3.eth.accounts
        if not accounts:
            raise RuntimeError("No accounts available on local Ganache node.")

        sender_account = accounts[0]
        private_key = Config.BLOCKCHAIN_PRIVATE_KEY

        try:
            # Check if private key matches an account or use default sender
            if private_key and len(private_key) == 66 and private_key.startswith("0x"):
                account = self.w3.eth.account.from_key(private_key)
                sender_address = account.address
                nonce = self.w3.eth.get_transaction_count(sender_address)

                tx = self.contract.functions.registerCertificate(
                    certificate_id,
                    certificate_hash,
                    issuer,
                    timestamp
                ).build_transaction({
                    'from': sender_address,
                    'nonce': nonce,
                    'gas': 3000000,
                    'gasPrice': self.w3.eth.gas_price
                })

                signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
                raw_tx = getattr(signed_tx, 'raw_transaction', getattr(signed_tx, 'rawTransaction', None))
                tx_hash = self.w3.eth.send_raw_transaction(raw_tx)
                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                return tx_receipt.transactionHash.hex()
            else:
                # Direct unlock on Ganache node
                tx_hash = self.contract.functions.registerCertificate(
                    certificate_id,
                    certificate_hash,
                    issuer,
                    timestamp
                ).transact({'from': sender_account, 'gas': 3000000})

                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                return tx_receipt.transactionHash.hex()

        except Exception as e:
            error_msg = str(e)
            if "already registered" in error_msg:
                raise ValueError("Certificate ID already registered on the blockchain.")
            raise RuntimeError(f"Blockchain transaction failed: {error_msg}")

    def verify_certificate_on_chain(self, certificate_id: str, certificate_hash: str) -> bool:
        """
        Queries the smart contract to verify if the given hash matches the on-chain record.
        """
        if not self.is_connected() or not self.contract:
            raise ConnectionError("Blockchain service or contract unavailable.")

        try:
            is_valid = self.contract.functions.verifyCertificate(certificate_id, certificate_hash).call()
            return is_valid
        except Exception as e:
            print(f"[!] Blockchain verification error: {e}")
            return False

    def get_certificate_from_chain(self, certificate_id: str) -> dict:
        """
        Retrieves stored record details directly from the blockchain.
        """
        if not self.is_connected() or not self.contract:
            raise ConnectionError("Blockchain service or contract unavailable.")

        try:
            result = self.contract.functions.getCertificate(certificate_id).call()
            return {
                'certificate_hash': result[0],
                'issuer': result[1],
                'timestamp': result[2],
                'registered_by': result[3]
            }
        except Exception as e:
            print(f"[!] Error fetching certificate from chain: {e}")
            return None

# Singleton instance
blockchain_service = BlockchainService()
