# it10bb_smart_estimator.py
# Smart rough estimator for IT-10BB expense sections (Bangladesh).
# Inputs: total annual expense (BDT), location (dhaka/other), family size, has_kids, own_home, home_support_staff, mode.
# Output: percentage + amount per IT-10BB section (rounded).

def compute_allocation(total_expense,
                       location='other_area',
                       family_size=3,
                       has_kids=True,
                       own_home=False,
                       home_support_staff=False,
                       mode='balanced'):
    """
    mode: 'balanced' (default), 'conservative' (cut festival/home support), 'comfortable' (more festival/home support)
    """
    # Base heuristic weights (intuitive starting point)
    weights = {
        "Food, Clothing and Other Essentials": 30.0,
        "Accommodation Expense": 28.0,
        "Electricity": 4.0,
        "Gas, Water, Sewer and Garbage": 3.0,
        "Phone, Internet, TV channels & Subscriptions": 4.0,
        "Home-Support Staff and Other Expenses": 6.0,
        "Education Expenses (for kids)": 10.0,
        "Festival, Party, Events": 5.0
    }

    # Remove education if no kids
    if not has_kids:
        weights["Education Expenses (for kids)"] = 0.0

    # Location modifiers
    loc = location.strip().lower()
    if loc in ('dhaka', 'dhaka_city', 'city', 'big_city', 'metro'):
        # Dhaka = higher rent + slightly higher living costs
        weights["Accommodation Expense"] *= 1.20
        weights["Food, Clothing and Other Essentials"] *= 1.05
        weights["Phone, Internet, TV channels & Subscriptions"] *= 1.05
        weights["Home-Support Staff and Other Expenses"] *= 1.10
    else:
        # smaller towns: slightly lower accommodation
        weights["Accommodation Expense"] *= 0.90

    # Family size effect: every additional person above 2 increases food & education demand
    extra_people = max(0, int(family_size) - 2)
    if extra_people > 0:
        weights["Food, Clothing and Other Essentials"] *= (1 + 0.05 * extra_people)
        if has_kids:
            weights["Education Expenses (for kids)"] *= (1 + 0.04 * extra_people)

    # Own home: typically less rent, some maintenance still exists
    if own_home:
        weights["Accommodation Expense"] *= 0.60
        weights["Home-Support Staff and Other Expenses"] *= 1.05

    # Home support presence
    if not home_support_staff:
        weights["Home-Support Staff and Other Expenses"] *= 0.4

    # Mode tweaks
    if mode == 'conservative':
        weights["Festival, Party, Events"] *= 0.6
        weights["Home-Support Staff and Other Expenses"] *= 0.7
        weights["Food, Clothing and Other Essentials"] *= 1.08
    elif mode == 'comfortable':
        weights["Festival, Party, Events"] *= 1.3
        weights["Home-Support Staff and Other Expenses"] *= 1.2
        weights["Food, Clothing and Other Essentials"] *= 1.05
    # else 'balanced' -> no extra change

    # Normalize to 100% across included categories
    total_weight = sum([w for w in weights.values() if w > 0])
    percentages = {}
    for k, w in weights.items():
        percentages[k] = round((w / total_weight) * 100.0, 2) if w > 0 else 0.0

    # Fix tiny rounding drift by adjusting the largest category
    drift = round(100.0 - sum(percentages.values()), 2)
    if abs(drift) >= 0.01:
        largest = max(percentages, key=lambda k: percentages[k])
        percentages[largest] = round(percentages[largest] + drift, 2)

    # Compute amounts
    amounts = {k: round(total_expense * (percentages[k] / 100.0), 2) for k in percentages}

    return percentages, amounts


def print_breakdown(percentages, amounts, total_expense):
    print("\n======= IT-10BB Rough Expense Breakdown =======")
    for k in percentages:
        print(f"{k:<45} : {percentages[k]:6.2f}% | Tk {amounts[k]:,.2f}")
    print("------------------------------------------------")
    print(f"{'TOTAL':<45} : {sum(percentages.values()):6.2f}% | Tk {total_expense:,.2f}")
    print("================================================\n")


if __name__ == "__main__":
    print("Smart IT-10BB Rough Expense Estimator\n")
    try:
        total = float(input("Enter total annual expenses (BDT): ").strip())
    except ValueError:
        print("Invalid total. Please enter a number.")
        raise SystemExit

    loc = input("Location (dhaka / other_area) [default other_area]: ").strip() or 'other_area'
    try:
        fam = int(input("Family size (number of people) [default 3]: ").strip() or "3")
    except ValueError:
        fam = 3
    kids = input("Do you have kids? (y/N) [default N]: ").strip().lower() == 'y'
    own = input("Own home (no rent)? (y/N) [default N]: ").strip().lower() == 'y'
    staff = input("Have home-support staff (driver/housemaid)? (y/N) [default N]: ").strip().lower() == 'y'
    mode = input("Mode (balanced/conservative/comfortable) [default balanced]: ").strip().lower() or 'balanced'

    pct, amt = compute_allocation(total, loc, fam, kids, own, staff, mode)
    print_breakdown(pct, amt, total)
