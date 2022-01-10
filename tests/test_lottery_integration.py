# Use Rinkeby testnet for integration tests
from brownie import network
import pytest
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_with_link,
)
from scripts.deploy_lottery import deploy_lottery
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("This test is only for local blockchain environments")
    # Arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enterLottery({"from": account, "value": lottery.getEntranceFee()})
    lottery.enterLottery({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery.address)

    # Act
    lottery.endLottery({"from": account})
    # When running on a testnet we just have to wait for the block to be mined
    time.sleep(180)

    # Assert
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
