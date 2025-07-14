def write_transaction_to_csv(account_id, writer, transaction):
    writer.writerow(
        (
            account_id,
            transaction["date"],
            transaction["description"],
            transaction["provider_transaction_id"],
            transaction["amount"],
            transaction["id"],
        )
    )
