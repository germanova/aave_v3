from scripts.helpful_scripts import get_account
from brownie import interface, config, network


def main():
    get_weth_eth()


def get_weth_eth():
    """
    Mints WETH by depositing ETH
    """
    # ABI
    # Address
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    amount = 0.1
    tx = weth.deposit({"from": account, "value": amount * 10**18})
    tx.wait(1)
    print("Recieved ", amount, " WETH")
    return tx


# if you want to convert weth to eth you can use the withdraw function (reference at etherscan validated contract functions)


def get_weth_op(eth_amount):
    """
    Mints WETH by depositing ETH
    """
    # ABI
    # Address
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    eth_usd = get_asset_price(
        config["networks"][network.show_active()]["eth_usd_price_feed"], "ETH/USD"
    )
    op_usd = get_asset_price(
        config["networks"][network.show_active()]["op_usd_price_feed"], "OP/USD"
    )
    # we are using optimism forked network, but we want to specify the value in ETH so that we use the
    # same amount as in goerli testnet. Nevertheless, Aave V3 shows account data in USD
    op_eth = eth_usd / op_usd
    op_amount = eth_amount * op_eth
    print(f"OP/ETH Coversion Rate is: {op_eth}, thus converted amount is {op_amount}")
    print(
        f"USD amount is: {eth_usd*eth_amount*10**-8}, it should be the same as Aave deposited amount"
    )
    tx = weth.deposit({"from": account, "value": op_amount * 10**18})
    tx.wait(1)
    print("Recieved ", eth_amount, " WETH")
    return tx


def get_asset_price(price_feed_address, label):
    # ABI
    # Address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]  # price is at index 1
    print(f"{label} Coversion Rate is: {latest_price*10**-8}")
    return float(latest_price)
