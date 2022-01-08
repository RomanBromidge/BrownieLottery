// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

// Ownable denotes a contract that has an owner.
contract Lottery is VRFConsumerBase, Ownable {
    address payable[] public players;
    address payable public recentWinner;
    uint256 public randomness;
    uint256 public usdEntryFee;
    AggregatorV3Interface public ethUsdPriceFeed;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lotteryState;

    // Oracle fee for using Chainlink's VRF to calculate the winner using a random number
    uint256 public fee;
    // Key hash for the VRF
    bytes32 public keyHash;

    constructor(
        address _priceFeedAddress,
        address _VRFCoordinator,
        address _linkToken,
        uint256 _fee,
        bytes32 _keyHash
    ) public VRFConsumerBase(_VRFCoordinator, _linkToken) {
        usdEntryFee = 50 * (10**18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lotteryState = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyHash = _keyHash;
    }

    function enter() public payable {
        // $50 mimumum entry fee
        require(lotteryState == LOTTERY_STATE.OPEN);
        require(
            msg.value >= getEntranceFee(),
            "Not enough ETH to pay entry fee"
        );
        // In Solidity 0.7.0+ msg.sender is not automatically payable, so must be casted.
        players.push(payable(msg.sender));
    }

    function getEntranceFee() public view returns (uint256) {
        // Get the price of 1 ETH in USD from the aggregator
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        // Convert the eth price to uint256 and ensure it has the right number of decimals
        uint256 ethPrice = uint256(price * 10**10); // 18 decimals
        uint256 precision = 1 * 10**18;
        return (usdEntryFee * precision) / ethPrice;
    }

    function startLottery() public onlyOwner {
        require(
            lotteryState == LOTTERY_STATE.CLOSED,
            "Can't start a new lottery"
        );
        lotteryState = LOTTERY_STATE.OPEN;
    }

    function endLottery() public {
        require(lotteryState == LOTTERY_STATE.OPEN);
        lotteryState = LOTTERY_STATE.CALCULATING_WINNER;
        // Insecure randomness always leads to bad things happening!!! Use a secure randomness solution like Chainlink VRF
        // First the random number is requested from the chainlink VRF, which happens if the contract has enough LINK to pay the fee
        bytes32 requestId = requestRandomness(keyHash, fee);
    }

    // Once the chain has created a random number, this function is called to fulfill the request for a random number
    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(
            lotteryState == LOTTERY_STATE.CALCULATING_WINNER,
            "You are not ready to calculate"
        );
        require(_randomness > 0, "Randomness not found");
        // Mod the random number by the number of players to get the winner
        uint256 winnerIndex = _randomness % players.length;
        recentWinner = players[winnerIndex];
        // Transfer the balance to the winner
        recentWinner.transfer(address(this).balance);
        // Reset and close the lottery
        players = new address payable[](0);
        lotteryState = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}
