def create_bank():
    accounts = {}

    def create_account(account_id, initial_balance=0):
        if account_id in accounts:
            raise ValueError("Account ID already exists")
        accounts[account_id] = initial_balance

        def deposit(amount):
            nonlocal accounts
            if amount > 0:
                accounts[account_id] += amount

        def withdraw(amount):
            nonlocal accounts
            # Intentional bug: should check if accounts[account_id] >= amount but it checks accounts[account_id] > amount
            if accounts[account_id] > amount:
                accounts[account_id] -= amount
                return amount
            else:
                raise ValueError("Insufficient funds")

        def transfer_to(other_account_id, amount):
            nonlocal accounts
            if accounts[account_id] >= amount:
                accounts[account_id] -= amount
                accounts[other_account_id] += amount
            else:
                raise ValueError("Insufficient funds")

        def get_balance():
            return accounts[account_id]

        return deposit, withdraw, transfer_to, get_balance

    return create_account
