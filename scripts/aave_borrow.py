from scripts.helpful_scripts import get_account, FORKED_LOCAL_ENVIRONMENTS
from brownie import network, config, interface
from scripts.get_weth import get_weth_op, get_asset_price
from web3 import Web3

eth_amount = 0.001
eth_wei_amount = Web3.toWei(eth_amount, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
        get_weth_op(eth_amount)
    else:
        print("using testnet, WETH must be exchanged before to proceed")
    # ABI
    # Address
    pool = get_pool()
    print("pool address: ", pool)
    # Approve sending our ERC20 tokens
    approve_erc20(eth_wei_amount, pool.address, erc20_address, account)
    print("Depositing...")
    tx = pool.supply(
        erc20_address,
        eth_wei_amount,
        account.address,
        0,
        {"from": account},  # ,"gas_limit": 100000,  "allow_revert": True
    )
    tx.wait(1)
    print("Deposited")

    # How much can we borrow?
    borrowable_usd, total_debt = get_borrowable_data(pool, account)

    print("Borrowing...")
    dai_usd = get_asset_price(
        config["networks"][network.show_active()]["dai_usd_price_feed"], "DAI/USD"
    )
    dai_usd = dai_usd * 10**-8
    amount_to_borrow = (dai_usd) * (
        borrowable_usd * 0.8
    )  # 0.8 is used as a buffer, to maker suer our health factor is 'better'
    print(f"Borrowing {amount_to_borrow} DAI")
    dai_address = config["networks"][network.show_active()]["dai_token"]
    # 1 is for stable, 2 for variable interest rate
    borrow_tx = pool.borrow(
        dai_address,
        Web3.toWei(amount_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print(amount_to_borrow, " DAI Borrowed")
    get_borrowable_data(pool, account)
    repay_all(amount_to_borrow, pool, account)
    get_borrowable_data(pool, account)


def repay_all(amount, pool, account):
    token_address = config["networks"][network.show_active()]["dai_token"]
    approve_erc20(Web3.toWei(amount, "ether"), pool.address, token_address, account)
    # same rate type as specified in pool.borrow()
    print("repaying...")
    # -1 in amount to repay the entire debt, or you can use Web3.toWei(amount, "ether") if is an instant borrow
    repay_tx = pool.repay(
        token_address,
        Web3.toWei(amount, "ether"),
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("DAI Repaid")
    print("Deposited, Borrowed and repaid with Aave, Brownie and Chainlink")


def get_borrowable_data(pool, account):
    (
        totalCollateralBase,
        totalDebtBase,
        availableBorrowsBase,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = pool.getUserAccountData(account.address)
    availableBorrowsBase = Web3.fromWei(availableBorrowsBase, "ether") * 10**10
    totalCollateralBase = Web3.fromWei(totalCollateralBase, "ether") * 10**10
    totalDebtBase = Web3.fromWei(totalDebtBase, "ether") * 10**10
    print(f"You have {totalCollateralBase} worth USD deposited")
    print(f"You have {totalDebtBase} worth USD borrowed")
    print(f"You can borrow {availableBorrowsBase} worth of USD")
    return (float(availableBorrowsBase), float(totalDebtBase))


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("ERC20 Token Approved")
    # ABI
    # Address


def get_pool():
    # Address
    pool_addresses_provider = interface.IPoolAddressesProvider(
        config["networks"][network.show_active()]["pool_addresses_provider"]
    )
    pool_address = pool_addresses_provider.getPool()

    # ABI
    pool = interface.IPool(pool_address)
    return pool
