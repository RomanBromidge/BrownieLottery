Users can enter the lottery with ETH based on a minimum USD fee
An admin will choose when the lottery takes place (admin is centralised, could alternatively have a DAO do it or based on time parameters i.e. Chainlink Keepers)
The lottery will select a random winner


How do we want to test this?

1) `mainnet-fork`
2) `development-with-mocks`
3) `testnet`


Useful commands:
To add a network to brownie for testing
`brownie networks add development <name> cmd=ganache-cli host=http://127.0.0.1:8545 fork=<amplify url> accounts=10 mnemonic=brownie`