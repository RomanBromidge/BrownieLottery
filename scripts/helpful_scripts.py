from brownie import (
    network,
    accounts,
    config,
    MockV3Aggregator,
    MockVRFCoordinator,
    Contract,
)
from web3 import Web3

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

DECIMALS = 8
STARTING_PRICE = 200000000000


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


def deploy_mocks(decimals=DECIMALS, starting_price=STARTING_PRICE):
    print("Deploying mocks...")
    MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": get_account()})
    print("Mocks deployed at: ", MockV3Aggregator[-1].address)


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": MockVRFCoordinator,
}


def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config if defined, otherwise it will deploy a mock version of that contract and return that mock contract

    args:
        contract_name (str): the name of the contract you want to deploy

    returns:
        brownie.network.contract.ProjectContract: the most recently deployed version of this contract
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # Check to see if there is an existing mock
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type._abi
        )
    return contract
