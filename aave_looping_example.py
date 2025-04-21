import requests
from web3 import Web3
from eth_account import Account

COMPASS_API_URL = 'https://api.compasslabs.ai'
PRIVATE_KEY = <YOUR_PRIVATE_KEY>
RPC_URL = <ETH_MAINNET_RPC_URL>
w3 = Web3.HTTPProvider(RPC_URL)

batch_call_and_sponsor_address = <BATCH_CALL_AND_SPONSOR_ADDRESS>
sender = <SENDER_ADDRESS>

# Payload for obtaining authorization
auth_payload = {
    'chain': 'ethereum:mainnet',
    'address': batch_call_and_sponsor_address,
    'sender': sender
}

auth_response = requests.post(f"{COMPASS_API_URL}/multicall/authorization", json=auth_payload)
auth = auth_response.json()

# Sign authorization with a private key
signed_auth = Account.sign_authorization(auth, PRIVATE_KEY)


# Construct AAVE looping payload:
# Swapping 100 USDC to 80 sUSDe
# Supplying 80 sUSDe
# Borrowing 50 USDC
batch_payload = {
    "chain": "ethereum:mainnet",
    "sender": sender,
    "signed_authorization": signed_auth.recursive_model_dump(),
    "actions": [
        {
            "action_type": "UNISWAP_SELL_EXACTLY",
            "body": {
                "amount_out_minimum": "80",
                "amount_in": "100",
                "fee": "0.05",
                "token_in": "USDC",
                "token_out": "sUSDe",
            },
        },
        {
            "action_type": "AAVE_SUPPLY",
            "body": {
                "amount": "80",
                "asset": "sUSDe",
            },
        },
        {
            "action_type": "AAVE_BORROW",
            "body": {
                "amount": "50",
                "asset": "USDC",
                "interest_rate_mode": "variable",
            },
        },
    ],
}
batch_response = requests.post(f"{COMPASS_API_URL}/multicall/execute", json=batch_payload)
batch_tx = batch_response.json()

# Sign EIP7702 transaction
signed_batch_tx = Account.sign_transaction(
    batch_tx, PRIVATE_KEY
)

# Broadcast the transaction
tx_hash = w3.eth.send_raw_transaction(signed_batch_tx.raw_transaction)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)