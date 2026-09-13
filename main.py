"""Cafe ordering system.

A command line till for a small drinks cafe. Takes an order of one or more
items, applies size pricing and discount codes, handles payment and change,
and writes an itemised receipt to receipt.txt.
"""

from datetime import datetime

try:
    from pyfiglet import Figlet
    FIGLET = Figlet(font="avatar")
except ImportError:
    FIGLET = None


# Menu and pricing

MENU = {
    "1": ("Water", 1.00),
    "2": ("Juice", 1.50),
    "3": ("Coffee", 2.00),
    "4": ("Tea", 1.50),
    "5": ("Milkshake", 2.50),
}

SIZES = {
    "small": 0.00,
    "medium": 0.50,
    "large": 1.00,
}

# Discount codes mapped to the percentage they take off the order.
DISCOUNT_CODES = {
    "CODE5": 5,
    "CODE10": 10,
    "STUDENT": 15,
}

WATER_TYPES = {
    "1": "Regular",
    "2": "Sparkling",
}

RECEIPT_FILE = "receipt.txt"
STAFF_PASSWORD = "Lock123"
MAX_ATTEMPTS = 3


# Input helpers

def banner(text):
    """Print a big ASCII banner, falling back to plain text if pyfiglet
    is not installed."""
    if FIGLET:
        print(FIGLET.renderText(text))
    else:
        print(f"\n=== {text.upper()} ===\n")


def ask_choice(prompt, valid_options):
    """Keep asking until the user enters one of valid_options.

    Input is lowercased and stripped so 'Large ' and 'large' both work.
    """
    while True:
        answer = input(prompt).strip().lower()
        if answer in valid_options:
            return answer
        print(f"Invalid input. Please enter one of: {', '.join(valid_options)}")


def ask_quantity(prompt):
    """Keep asking until the user enters a positive whole number."""
    while True:
        answer = input(prompt).strip()
        if answer.isdigit() and int(answer) > 0:
            return int(answer)
        print("Invalid input. Please enter a whole number of 1 or more.")


def ask_money(prompt):
    """Keep asking until the user enters a valid non negative amount."""
    while True:
        answer = input(prompt).strip().lstrip("£")
        try:
            amount = float(answer)
        except ValueError:
            print("Invalid input. Please enter an amount, for example 5.00")
            continue
        if amount < 0:
            print("Amount cannot be negative.")
            continue
        return round(amount, 2)


# Ordering

def show_menu():
    print("\nMenu")
    for key, (name, price) in MENU.items():
        print(f"  {key}. {name:<10} £{price:.2f}")
    print("  Sizes: small (+£0.00), medium (+£0.50), large (+£1.00)")


def take_item():
    """Collect one line of the order and return it as a dict."""
    show_menu()

    choice = ask_choice(
        "Please enter a number between 1 and 5: ", list(MENU)
    )
    name, base_price = MENU[choice]

    # Water has a sub choice, everything else does not.
    if name == "Water":
        print("  1. Regular water")
        print("  2. Sparkling water")
        water_choice = ask_choice("Enter your choice (1 or 2): ", list(WATER_TYPES))
        name = f"{WATER_TYPES[water_choice]} water"

    size = ask_choice("Would you like a small, medium or large? ", list(SIZES))
    quantity = ask_quantity("How many would you like? ")

    unit_price = base_price + SIZES[size]
    line_total = round(unit_price * quantity, 2)

    print(f"Added: {quantity} x {size} {name} at £{unit_price:.2f} = £{line_total:.2f}")

    return {
        "name": f"{size.title()} {name}",
        "unit_price": unit_price,
        "quantity": quantity,
        "line_total": line_total,
    }


def take_order():
    """Loop until the customer has finished adding items."""
    order = []
    while True:
        order.append(take_item())
        again = ask_choice("Would you like to order anything else? (yes/no): ",
                           ["yes", "no", "y", "n"])
        if again in ("no", "n"):
            break
    return order


def apply_discount(subtotal):
    """Ask for a discount code and return (percentage_off, amount_off)."""
    code = input("Please enter your discount code (or press Enter to skip): ")
    code = code.strip().upper()

    if not code:
        return 0, 0.00

    if code in DISCOUNT_CODES:
        percent = DISCOUNT_CODES[code]
        amount_off = round(subtotal * percent / 100, 2)
        print(f"Discount code accepted: {percent}% off, saving £{amount_off:.2f}")
        return percent, amount_off

    print("Error: invalid discount code. No discount applied.")
    return 0, 0.00


def take_payment(total):
    """Keep asking for money until the customer has paid enough.
    Returns the change owed."""
    while True:
        paid = ask_money(f"Total to pay is £{total:.2f}. Enter the amount you are paying: ")
        if paid < total:
            shortfall = round(total - paid, 2)
            print(f"That is not enough, you are £{shortfall:.2f} short. Please try again.")
            continue
        change = round(paid - total, 2)
        if change > 0:
            print(f"Thank you. Your change is £{change:.2f}")
        else:
            print("Thank you, exact amount received.")
        return change


# Receipt

def build_receipt(customer, order, subtotal, percent, amount_off, total, change):
    """Build the receipt as a single string so it can be printed and saved."""
    lines = []
    lines.append("=" * 52)
    lines.append("THE CAFE".center(52))
    lines.append(datetime.now().strftime("%d/%m/%Y  %H:%M").center(52))
    lines.append("=" * 52)
    lines.append(f"Customer: {customer}")
    lines.append("-" * 52)
    lines.append(f"{'Item':<22}{'Unit':>8}{'Qty':>6}{'Total':>10}")
    lines.append("-" * 52)

    for line in order:
        lines.append(
            f"{line['name']:<22}"
            f"{'£' + format(line['unit_price'], '.2f'):>8}"
            f"{line['quantity']:>6}"
            f"{'£' + format(line['line_total'], '.2f'):>10}"
        )

    lines.append("-" * 52)
    lines.append(f"{'Subtotal':<36}{'£' + format(subtotal, '.2f'):>16}")

    if amount_off > 0:
        lines.append(f"{f'Discount ({percent}%)':<36}{'-£' + format(amount_off, '.2f'):>16}")

    lines.append(f"{'TOTAL':<36}{'£' + format(total, '.2f'):>16}")
    lines.append(f"{'Change given':<36}{'£' + format(change, '.2f'):>16}")
    lines.append("=" * 52)
    lines.append("Thank you for shopping with us".center(52))
    lines.append("=" * 52)

    return "\n".join(lines)


def save_receipt(text):
    """Append the receipt to the receipt file so earlier orders are kept."""
    with open(RECEIPT_FILE, "a", encoding="utf-8") as file:
        file.write(text)
        file.write("\n\n")
    print(f"\nReceipt saved to {RECEIPT_FILE}")


# Staff mode

def staff_login():
    """Simple staff check with a limited number of attempts.

    Note: this is a coursework level check only. A real system would never
    store a password in the source code.
    """
    attempts = MAX_ATTEMPTS
    while attempts > 0:
        password = input("Staff password: ")
        if password == STAFF_PASSWORD:
            print("Password correct. Access granted.")
            return True
        attempts -= 1
        if attempts > 0:
            print(f"Incorrect password. You have {attempts} attempts left.")
    print("No attempts left. Access denied.")
    return False


# Main

def main():
    banner("Welcome")

    customer = input("Please enter your first name: ").strip() or "Guest"
    print(f"Hello, {customer}!")

    order = take_order()

    subtotal = round(sum(line["line_total"] for line in order), 2)
    print(f"\nSubtotal: £{subtotal:.2f}")

    percent, amount_off = apply_discount(subtotal)
    total = round(subtotal - amount_off, 2)

    change = take_payment(total)

    banner("Receipt")
    receipt = build_receipt(customer, order, subtotal, percent, amount_off, total, change)
    print(receipt)
    save_receipt(receipt)

    check = ask_choice("\nStaff: view today's saved receipts? (yes/no): ",
                       ["yes", "no", "y", "n"])
    if check in ("yes", "y") and staff_login():
        with open(RECEIPT_FILE, encoding="utf-8") as file:
            print("\n" + file.read())


if __name__ == "__main__":
    main()
