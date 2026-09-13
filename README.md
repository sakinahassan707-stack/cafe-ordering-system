# Cafe Ordering System

A command line till for a small drinks cafe, written in Python. Takes a multi item
order, applies size pricing and discount codes, handles payment and change, and
writes an itemised receipt to a text file.

This started as a first year coursework project and has since been rewritten to fix
the bugs in the original and to separate the logic into functions.

## Demo

```
====================================================
                      THE CAFE
                 13/09/2026  20:04
====================================================
Customer: Mk
----------------------------------------------------
Item                      Unit   Qty     Total
----------------------------------------------------
Large Coffee             £3.00     2     £6.00
Small Sparkling water    £1.00     1     £1.00
----------------------------------------------------
Subtotal                                       £7.00
Discount (10%)                                -£0.70
TOTAL                                          £6.30
Change given                                   £3.70
====================================================
```

## Features

- Menu of five drinks with small / medium / large size pricing
- Order as many items as you like in one transaction
- Input validation on every prompt, invalid entries re-ask instead of crashing
- Percentage based discount codes (`CODE5`, `CODE10`, `STUDENT`)
- Payment loop that rejects underpayment and calculates change
- Itemised receipt printed to screen and appended to `receipt.txt`
- Staff password check with a limited number of attempts

## Running it

Requires Python 3.10 or later.

```bash
pip install pyfiglet
python main.py
```

`pyfiglet` is only used for the ASCII art banners. If it is not installed the
program falls back to plain text headings and still runs.

## What I fixed from the original version

The first version worked on the surface but had several bugs that meant whole
branches never executed:

- **The receipt file was always empty.** The file was opened with `open(..., "w")`
  but every receipt line used `print()`, which writes to the screen, not the file.
  The file now has its contents written to it properly, and is opened in append
  mode so earlier orders are not wiped on each run.
- **The item variable was being overwritten.** `product` was converted to an
  integer and then immediately reassigned to the size answer, so every later
  `if product == 1` check compared a string like `"large"` against a number and
  was never true. Item and size are now separate variables.
- **Comparing strings to integers.** `input()` returns a string, so `product == 1`
  was always false even before the overwrite. Menu keys are now strings throughout.
- **The discount was wrong.** The total after discount was calculated from a fresh
  `finalTotal = 0` rather than the actual order total, so it always printed `-1.0`.
  Discounts are now a percentage of the real subtotal.
- **A hardcoded `cost = 20`** was used for the payment check instead of the order
  total, so change was calculated against an unrelated number.
- **The sparkling water prompt ran for every drink**, not just water, because it sat
  outside its `if` block.
- **The whole ordering section was copy pasted** to allow a second order. It is now
  a loop, so any number of items can be ordered.
- **Quantity was never collected**, so the receipt printed the literal word
  "quantity". It is now asked for and multiplied into the line total.

## Known limitations

- The staff password is stored in the source file. This is fine for a coursework
  exercise but is not how real authentication should work.
- Prices use floats. A production till would use `Decimal` to avoid rounding drift.
