from brownie import Lottery, network, config
from scripts.helpful_scripts import get_account
from web3 import Web3


def test_get_entrance_fee():
    account = get_account()
    lottery = Lottery.deploy(
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        {"from": account},
    )
    # We could estimate ourself to make sure that the entrance fee is correct within bounds. On day of writing $50 = 0.014 ETH
    assert lottery.getEntranceFee() > Web3.toWei(0.013, "ether")
    assert lottery.getEntranceFee() < Web3.toWei(0.015, "ether")
