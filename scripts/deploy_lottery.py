from brownie import Lottery, config, network
from scripts.helpful_scripts import get_account, get_contract, fund_with_link


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    start_tx = lottery.startLottery({"from": account})
    start_tx.wait(1)
    print("Lottery started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    enter_tx = lottery.enterLottery({"from": account, "value": value})
    enter_tx.wait(1)
    print("Entered lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # Fund the lottery with LINK
    fund_tx = fund_with_link(lottery.address)
    fund_tx.wait(1)
    end_tx = lottery.endLottery({"from": account})
    end_tx.wait(1)
    print("Lottery ended!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
