import json
import math
import os
import sys

# Values used when no code and amount are typed on the command line.
CODE = "EUR"
AMOUNT = "250"

FOLDER = os.path.dirname(os.path.abspath(__file__))
RATES_FILE = os.path.join(FOLDER, "rates.txt")
RECEIPT_FILE = os.path.join(FOLDER, "receipt.json")


def load_rates(path):
    """Read CODE=RATE lines into a dictionary such as {"EUR": 1.08}."""
    rates = {}
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()  # text mode already turned "\r\n" into "\n"
            if line == "":
                continue
            code, rate = line.split("=")
            rates[code.strip().upper()] = float(rate)
    return rates


def parse_amount(text):
    """Turn the typed amount into a positive number, or raise ValueError."""
    try:
        amount = float(text)
    except ValueError:
        raise ValueError("Amount must be a number, got: " + str(text))
    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("Amount must be a positive number, got: " + str(text))
    return amount


def convert(amount, rate):
    """Dollars for this amount at this rate, rounded to cents."""
    return round(amount * rate, 2)


def make_receipt(code, amount_text, rates):
    """Build the receipt dictionary, or raise ValueError with a clear message."""
    code = code.strip().upper()
    if code not in rates:
        raise ValueError("Unknown currency code: " + code)
    amount = parse_amount(amount_text)
    rate = rates[code]
    return {
        "code": code,
        "amount": amount,
        "rate": rate,
        "usd_total": convert(amount, rate),
    }


def save_receipt(receipt, path):
    with open(path, "w", encoding="utf-8") as file:
        file.write(json.dumps(receipt, indent=2))


def load_receipt(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.loads(file.read())


def main(args):
    code = CODE
    amount_text = AMOUNT
    if len(args) == 2:
        code = args[0]
        amount_text = args[1]
    elif len(args) != 0:
        print("Error: type a code and an amount, for example: EUR 250")
        return 1

    try:
        rates = load_rates(RATES_FILE)
        receipt = make_receipt(code, amount_text, rates)
    except FileNotFoundError:
        print("Error: rates.txt was not found in the project folder")
        return 1
    except ValueError as error:
        print("Error: " + str(error))
        return 1

    print(f"{receipt['code']} {receipt['amount']:.2f} at {receipt['rate']} "
          f"= {receipt['usd_total']:.2f} USD")

    save_receipt(receipt, RECEIPT_FILE)
    stored = load_receipt(RECEIPT_FILE)
    print(f"Receipt saved. Stored dollar total: {stored['usd_total']:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))