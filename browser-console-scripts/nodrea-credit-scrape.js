(function scrapeCreditCardTransactions() {
  // Dear Nordea: I am reading my own credit card transactions
  // via this script because your web bank does not provide
  // credit card transactions in a machine-readable format.
  const transactions = [];
  for (const element of document.querySelectorAll('.transaction-row')) {
    transactions.push({
      date: element.querySelector('#transactionDate').innerText,
      title: element.querySelector('#transactionTitle').innerText,
      amount: element.querySelector('#transactionAmount').innerText,
    });
  }
  copy(JSON.stringify(transactions, null, 2));
})();
