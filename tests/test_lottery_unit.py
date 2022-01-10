from brownie import Lottery, network, config, exceptions
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_with_link,
    get_contract,
)
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3
import pytest


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("This test is only for local blockchain environments")

    # Arrange
    lottery = deploy_lottery()

    # Act
    # 2000 usd / eth
    # usdEntranceFee is $50
    # ethEntranceFee is $0.025
    expected_entrace_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()

    # Assert
    assert entrance_fee == expected_entrace_fee


def test_cannot_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("This test is only for local blockchain environments")

    # Arrange
    lottery = deploy_lottery()

    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enterLottery({"from": get_account()})


def test_can_start_and_enter_lotter():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("This test is only for local blockchain environments")

    # Arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})

    # Act
    lottery.enterLottery({"from": account, "value": lottery.getEntranceFee()})

    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("This test is only for local blockchain environments")

    # Arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enterLottery({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery.address)

    # Act
    lottery.endLottery({"from": account})

    # Assert
    assert lottery.lotteryState() == 2


def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("This test is only for local blockchain environments")
    # Arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enterLottery({"from": account, "value": lottery.getEntranceFee()})
    lottery.enterLottery(
        {"from": get_account(index=1), "value": lottery.getEntranceFee()}
    )
    lottery.enterLottery(
        {"from": get_account(index=2), "value": lottery.getEntranceFee()}
    )
    fund_with_link(lottery.address)
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()

    # Act
    txn = lottery.endLottery({"from": account})
    request_id = txn.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address
    )

    # Assert
    # Since 777 % 3 == 0, the winner is the first player
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery
