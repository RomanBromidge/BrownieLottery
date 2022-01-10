from os import link
from brownie import (
    network,
    accounts,
    config,
    MockV3Aggregator,
    MockVRFCoordinator,
    MockLinkToken,
    Contract,
    interface,
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
    link_token = MockLinkToken.deploy({"from": get_account()})
    MockVRFCoordinator.deploy(link_token.address, {"from": get_account()})
    print("Mocks deployed!")


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": MockVRFCoordinator,
    "link_token": MockLinkToken,
}


def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config if defined, otherwise it will deploy a mock version of that contract and return that mock contract

    args:
        contract_name (str): the name of the contract you want to deploy

    returns:
        brownie.network.contract.ProjectContract: the most recently deployed version of this contract
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # Check to see if there is an existing mock
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def fund_with_link(
    contract_address,
    account=None,
    link_token=None,
    amount=100000000000000000,
):  # 0.1 LINK
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # Not totally sure why this is necessary, but it seems like the link token contract is not able to send transactions without it
        link_token.LinkToken({"from": account})
    # Two methods
    # 1)
    tx = link_token.transfer(contract_address, amount, {"from": account})

    # 2)
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})

    tx.wait(1)
    print("Funded with LINK")
    return tx
