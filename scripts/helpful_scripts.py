from brownie import (
    network,
    config,
    accounts,
)


FORKED_LOCAL_ENVIRONMENTS = ["optimism-mainnet-fork"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):

    if index:
        return accounts[index]
    elif (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]

    elif id:
        accounts.load(id)
    else:
        return accounts.load(config["wallets"]["account_name"])
