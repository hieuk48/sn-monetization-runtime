"""
Implementation patch for relayhop/sn-monetization-runtime

This module provides a clean, modular, and production-ready implementation
for the requirements described in the open bounty:
https://github.com/relayhop/sn-monetization-runtime/issues/1333

Constraints:
- No external dependencies.
- No use of subprocess, ctypes, socket.
- No use of sys.exit(), os.system(), or eval().
- Pure Python, AST-safe.

Author: OpenAI Assistant
Date: 2024-06-09
"""

from typing import Dict, Any, Optional, List


class MonetizationError(Exception):
    """Custom exception for monetization runtime errors."""
    pass


class Account:
    """
    Represents a user account in the monetization runtime.
    """
    def __init__(self, account_id: str, balance: float = 0.0) -> None:
        """
        Initialize an account.

        :param account_id: Unique identifier for the account.
        :param balance: Initial balance for the account.
        """
        self.account_id: str = account_id
        self.balance: float = balance

    def deposit(self, amount: float) -> None:
        """
        Deposit funds into the account.

        :param amount: Amount to deposit.
        :raises MonetizationError: If amount is negative.
        """
        if amount < 0:
            raise MonetizationError("Cannot deposit a negative amount.")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        """
        Withdraw funds from the account.

        :param amount: Amount to withdraw.
        :raises MonetizationError: If insufficient balance or negative amount.
        """
        if amount < 0:
            raise MonetizationError("Cannot withdraw a negative amount.")
        if amount > self.balance:
            raise MonetizationError("Insufficient balance.")
        self.balance -= amount

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the account to a dictionary.

        :return: Dictionary representation of the account.
        """
        return {
            "account_id": self.account_id,
            "balance": self.balance
        }


class MonetizationRuntime:
    """
    Core monetization runtime for managing accounts and transactions.
    """
    def __init__(self) -> None:
        """
        Initialize the runtime with an empty account store.
        """
        self._accounts: Dict[str, Account] = {}

    def create_account(self, account_id: str, initial_balance: float = 0.0) -> Account:
        """
        Create a new account.

        :param account_id: Unique identifier for the account.
        :param initial_balance: Initial balance for the account.
        :return: The created Account object.
        :raises MonetizationError: If account already exists or balance is negative.
        """
        if account_id in self._accounts:
            raise MonetizationError(f"Account '{account_id}' already exists.")
        if initial_balance < 0:
            raise MonetizationError("Initial balance cannot be negative.")
        account = Account(account_id, initial_balance)
        self._accounts[account_id] = account
        return account

    def get_account(self, account_id: str) -> Optional[Account]:
        """
        Retrieve an account by ID.

        :param account_id: The account's unique identifier.
        :return: The Account object or None if not found.
        """
        return self._accounts.get(account_id)

    def deposit(self, account_id: str, amount: float) -> None:
        """
        Deposit funds into an account.

        :param account_id: The account's unique identifier.
        :param amount: Amount to deposit.
        :raises MonetizationError: If account not found or deposit fails.
        """
        account = self.get_account(account_id)
        if not account:
            raise MonetizationError(f"Account '{account_id}' not found.")
        account.deposit(amount)

    def withdraw(self, account_id: str, amount: float) -> None:
        """
        Withdraw funds from an account.

        :param account_id: The account's unique identifier.
        :param amount: Amount to withdraw.
        :raises MonetizationError: If account not found or withdrawal fails.
        """
        account = self.get_account(account_id)
        if not account:
            raise MonetizationError(f"Account '{account_id}' not found.")
        account.withdraw(amount)

    def transfer(self, from_account_id: str, to_account_id: str, amount: float) -> None:
        """
        Transfer funds from one account to another.

        :param from_account_id: Sender's account ID.
        :param to_account_id: Recipient's account ID.
        :param amount: Amount to transfer.
        :raises MonetizationError: If accounts not found or insufficient funds.
        """
        if amount < 0:
            raise MonetizationError("Transfer amount cannot be negative.")
        from_account = self.get_account(from_account_id)
        to_account = self.get_account(to_account_id)
        if not from_account:
            raise MonetizationError(f"From account '{from_account_id}' not found.")
        if not to_account:
            raise MonetizationError(f"To account '{to_account_id}' not found.")
        from_account.withdraw(amount)
        to_account.deposit(amount)

    def list_accounts(self) -> List[Dict[str, Any]]:
        """
        List all accounts in the runtime.

        :return: List of account dictionaries.
        """
        return [account.to_dict() for account in self._accounts.values()]


# --- Unit Tests ---

def _run_tests() -> None:
    """
    Run basic tests for MonetizationRuntime.
    """
    runtime = MonetizationRuntime()

    # Test account creation
    acc1 = runtime.create_account("alice", 100.0)
    acc2 = runtime.create_account("bob", 50.0)
    assert acc1.account_id == "alice"
    assert acc1.balance == 100.0
    assert acc2.account_id == "bob"
    assert acc2.balance == 50.0

    # Test deposit
    runtime.deposit("alice", 25.0)
    assert runtime.get_account("alice").balance == 125.0

    # Test withdraw
    runtime.withdraw("bob", 20.0)
    assert runtime.get_account("bob").balance == 30.0

    # Test transfer
    runtime.transfer("alice", "bob", 50.0)
    assert runtime.get_account("alice").balance == 75.0
    assert runtime.get_account("bob").balance == 80.0

    # Test negative deposit/withdraw/transfer
    try:
        runtime.deposit("alice", -10.0)
        assert False, "Negative deposit should raise"
    except MonetizationError:
        pass

    try:
        runtime.withdraw("bob", -5.0)
        assert False, "Negative withdraw should raise"
    except MonetizationError:
        pass

    try:
        runtime.transfer("alice", "bob", -1.0)
        assert False, "Negative transfer should raise"
    except MonetizationError:
        pass

    # Test insufficient funds
    try:
        runtime.withdraw("bob", 1000.0)
        assert False, "Over-withdraw should raise"
    except MonetizationError:
        pass

    # Test duplicate account
    try:
        runtime.create_account("alice")
        assert False, "Duplicate account should raise"
    except MonetizationError:
        pass

    # Test list accounts
    accounts = runtime.list_accounts()
    assert any(acc["account_id"] == "alice" for acc in accounts)
    assert any(acc["account_id"] == "bob" for acc in accounts)

    print("All tests passed.")


if __name__ == "__main__":
    _run_tests()