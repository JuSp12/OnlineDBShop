import sqlite3
from datetime import datetime


# Main menu display and options to call the functions
def main_menu(shopper_first_name, shopper_id):
    print(f"\nWelcome to the Online Shop, {shopper_first_name}!")
    print("\nSHOPPER MAIN MENU")

    while True:
        option = input("\n1. Display your order history\n"
                       "2. Add an item to your basket\n"
                       "3. View your basket\n"
                       "4. Change the quantity of an item in your basket\n"
                       "5. Remove an item from your basket\n"
                       "6. Checkout\n"
                       "7. Exit\n"
                       "Please select an option: ")
        print('')
        if option == "1":
            display_order_history(shopper_id)
        elif option == "2":
            add_item_to_basket(shopper_id)
        elif option == "3":
            display_basket(shopper_id)
        elif option == "4":
            change_the_qty(shopper_id)
        elif option == "5":
            remove_an_item(shopper_id)
        elif option == "6":
            checkout(shopper_id)
        elif option == "7":
            exit_program()
        else:
            print("Invalid option. Please try again.")


def display_order_history(shopper_id):
    conn = sqlite3.connect('Shop_database.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT o.order_id, o.order_date, p.product_description, s.seller_name, op.price, 
    op.quantity, op.ordered_product_status
FROM shopper_orders o
JOIN ordered_products op ON o.order_id = op.order_id
JOIN products p ON op.product_id = p.product_id
JOIN sellers s ON op.seller_id = s.seller_id
WHERE o.shopper_id = ?
ORDER BY o.order_date DESC""", (shopper_id,))
    order_history = cursor.fetchall()

    conn.close()

    if not order_history:
        print("\nNo orders placed by this customer")
        return

    print("\nOrder History:")
    print(
        "{:<10} {:<13} {:<70} {:<17} {:<10} {:<5} {:<10}".format("OrderID", "OrderDate",
                                                                 "ProductDescription", "Seller", "Price",
                                                                 "Qty", "Status"))
    for order in order_history:
        order_id, order_date, product_description, seller_name, price, quantity, ordered_product_status = order
        print("{:<10} {:<13} {:<70} {:<17} {:<10} {:<5} {:<10}".format(order_id, order_date, product_description,
                                                                       seller_name, price, quantity,
                                                                       ordered_product_status))


def add_item_to_basket(shopper_id):
    conn = sqlite3.connect('Shop_database.db')
    cursor = conn.cursor()

    # Display a numbered list of product categories
    cursor.execute("SELECT category_id, category_description FROM categories")
    categories = cursor.fetchall()
    print("Product Categories:")
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category[1]}")

    # Enter the number of the product category to choose from
    while True:
        category_choice = input("Enter the number of the product category you want to choose from: ")
        if category_choice.isdigit():
            category_choice = int(category_choice)
            if 1 <= category_choice <= len(categories):
                selected_category_id = categories[category_choice - 1][0]
                break
            else:
                print("Invalid category number. Please try again.")
        else:
            print("Invalid input. Please enter a number.")

    # Display a numbered list products in the selected category
    cursor.execute(
        "SELECT product_id, product_description FROM products "
        "WHERE category_id = ? AND product_status IN ('Available', 'Discontinued')",
        (selected_category_id,))
    available_products = cursor.fetchall()
    if not available_products:
        print("No available products in this category at the moment.")
        return

    print("\nAvailable Products:")
    for i, product in enumerate(available_products, 1):
        print(f"{i}. {product[1]}")

    # Enter the number of the product to purchase
    while True:
        product_choice = input("Enter the number of the product you want to purchase: ")
        if product_choice.isdigit():
            product_choice = int(product_choice)
            if 1 <= product_choice <= len(available_products):
                selected_product_id = available_products[product_choice - 1][0]
                break
            else:
                print("Invalid product number. Please try again.")
        else:
            print("Invalid input. Please enter a number.")

    # Display a numbered list of sellers selling the selected product and prices
    cursor.execute(
        "SELECT ps.seller_id, s.seller_name, ps.price FROM product_sellers ps "
        "JOIN sellers s ON ps.seller_id = s.seller_id WHERE ps.product_id = ?",
        (selected_product_id,))
    available_sellers = cursor.fetchall()

    if not available_sellers:
        print("No sellers available for this product.")
        return

    print("\nAvailable Sellers and Prices:")
    for i, seller in enumerate(available_sellers, 1):
        print(f"{i}. {seller[1]} - Price: £{seller[2]}")

    # Enter the number of the seller to buy from
    while True:
        seller_choice = input("Enter the number of the seller you wish to buy from: ")
        if seller_choice.isdigit():
            seller_choice = int(seller_choice)
            if 1 <= seller_choice <= len(available_sellers):
                selected_seller_id = available_sellers[seller_choice - 1][0]
                selected_price = available_sellers[seller_choice - 1][2]
                break
            else:
                print("Invalid seller number. Please try again.")
        else:
            print("Invalid input. Please enter a number.")

    # Enter the quantity of the selected product to order
    while True:
        quantity = input("Enter the quantity of the selected product you want to order: ")
        if quantity.isdigit() and int(quantity) > 0:
            break
        else:
            print("The quantity must be greater than 0. Please try again.")

    # Check if the product already exists in the basket for this shopper
    cursor.execute("""SELECT bc.basket_id
                      FROM basket_contents bc
                      JOIN shopper_baskets sb ON bc.basket_id = sb.basket_id
                      WHERE sb.shopper_id = ? AND bc.product_id = ?""",
                   (shopper_id, selected_product_id))
    existing_basket = cursor.fetchone()

    if existing_basket:
        print('Product already in the basket.')
        add_item_to_basket(shopper_id)  # Return to add_item_to_basket
        return

    # Check if the shopper already has a basket
    cursor.execute("SELECT basket_id FROM shopper_baskets WHERE shopper_id = ?", (shopper_id,))
    existing_basket = cursor.fetchone()

    if existing_basket:
        # Use the existing basket_id
        next_basket_id = existing_basket[0]
    else:
        # Find the maximum basket_id for this shopper_id and increment by 1, or start from 1 if no basket exists
        cursor.execute("SELECT MAX(basket_id) FROM shopper_baskets")
        max_basket_id = cursor.fetchone()[0]
        if max_basket_id is None:
            next_basket_id = 1
        else:
            next_basket_id = max_basket_id + 1

        # Insert a new row into the shopper_baskets table
        cursor.execute("INSERT INTO shopper_baskets (basket_id, shopper_id, basket_created_date_time) VALUES (?, ?, ?)",
                       (next_basket_id, shopper_id, datetime.now()))

    # Insert a new row into the basket_contents table
    cursor.execute(
        "INSERT INTO basket_contents (basket_id, product_id, seller_id, quantity, price) VALUES (?, ?, ?, ?, ?)",
        (next_basket_id, selected_product_id, selected_seller_id, quantity, selected_price))

    conn.commit()

    print("Item added to your basket.")

    conn.close()


def display_basket(shopper_id):
    conn = sqlite3.connect('Shop_database.db')
    cursor = conn.cursor()

    # Display basket contents and total cost
    cursor.execute("""SELECT bc.quantity, p.product_description, s.seller_name, bc.price
                      FROM basket_contents bc
                      JOIN products p ON bc.product_id = p.product_id
                      JOIN sellers s ON bc.seller_id = s.seller_id
                      JOIN shopper_baskets sb ON bc.basket_id = sb.basket_id
                      WHERE sb.shopper_id = ?""", (shopper_id,))
    basket_items = cursor.fetchall()

    if not basket_items:
        print("Your basket is empty.")
        return

    print("{:<10} {:<70} {:<20} {:<15} {:<10} {:<10}".format
          ("Item No.", "Product Description", "Seller", "Price", "Quantity", "Total Price"))
    print("-" * 145)
    total_cost = 0
    for i, (quantity, product_description, seller_name, price) in enumerate(basket_items, 1):
        total_price = quantity * price
        total_cost += total_price
        print("{:<10} {:<70} {:<20} {:<15} {:<10} {:<10}".format(i, product_description, seller_name, f"£{price:.2f}",
                                                                 quantity, f"£{total_price:.2f}"))

    print("-" * 145)
    print(f"Total Basket Cost: £{total_cost:.2f}")

    conn.close()


def change_the_qty(shopper_id):
    conn = sqlite3.connect('Shop_database.db')
    cursor = conn.cursor()

    # Check if the basket is empty
    cursor.execute("SELECT COUNT(*) FROM basket_contents "
                   "WHERE basket_id = (SELECT basket_id FROM shopper_baskets WHERE shopper_id = ?)",
                   (shopper_id,))
    basket_count = cursor.fetchone()[0]

    if basket_count == 0:
        print("Your basket is empty.")
        return

    # Display basket and total cost
    display_basket(shopper_id)

    # Enter the basket item number
    if basket_count >= 0:
        while True:
            basket_item_no = input("Enter the basket item number of the item you want to update: ")
            if basket_item_no.isdigit() and 1 <= int(basket_item_no) <= basket_count:
                break
            else:
                print("Invalid basket item number. Please try again.")

        # Enter the new quantity for the item selected
        new_quantity = int(input("Enter the new quantity: "))
        while new_quantity <= 0:
            print("The quantity must be greater than 0.")
            new_quantity = int(input("Enter the new quantity: "))

        # Get the basket ID
        cursor.execute("SELECT basket_id FROM shopper_baskets WHERE shopper_id = ?", (shopper_id,))
        basket_id = cursor.fetchone()[0]

        # Update the basket_contents table with the new quantity
        cursor.execute("UPDATE basket_contents SET quantity = ? "
                       "WHERE basket_id = ? AND product_id = (SELECT product_id FROM basket_contents "
                       "WHERE basket_id = ? AND rowid = ?)",
                       (new_quantity, basket_id, basket_id, basket_item_no))

        conn.commit()

        # Display the updated basket
        display_basket(shopper_id)

    conn.close()


def remove_an_item(shopper_id):
    conn = sqlite3.connect('Shop_database.db')
    cursor = conn.cursor()

    # Check if the basket is empty
    cursor.execute("SELECT COUNT(*) FROM basket_contents "
                   "WHERE basket_id = (SELECT basket_id FROM shopper_baskets WHERE shopper_id = ?)",
                   (shopper_id,))
    basket_count = cursor.fetchone()[0]

    if basket_count == 0:
        print("Your basket is empty.")
        return

    # Display basket and total cost
    display_basket(shopper_id)

    # Enter the basket item number
    if basket_count >= 1:
        while True:
            basket_item_no = input("Enter the basket item number of the item you want to remove: ")
            if basket_item_no.isdigit() and 1 <= int(basket_item_no) <= basket_count:
                break
            else:
                print("Invalid basket item number. Please try again.")

        print("Selected basket item number:", basket_item_no)

        # Prompt the user to confirm removal
        confirm = input("Are you sure you want to remove this item from your basket? (Y/N): ")
        if confirm.lower() == "y":
            # Get the basket ID
            cursor.execute("SELECT basket_id FROM shopper_baskets WHERE shopper_id = ?", (shopper_id,))
            basket_id = cursor.fetchone()[0]

            print("Selected basket ID:", basket_id)

            # Delete the item from the basket_contents table
            cursor.execute("DELETE FROM basket_contents WHERE basket_id = ? AND product_id = "
                           "(SELECT product_id FROM basket_contents "
                           "WHERE basket_id = ? AND rowid = ?)",
                           (basket_id, basket_id, basket_item_no))

            print("Item removed from the basket_contents table.")

            conn.commit()

            # Check if the basket is empty
            cursor.execute("SELECT COUNT(*) FROM basket_contents WHERE basket_id = ?", (basket_id,))
            basket_count = cursor.fetchone()[0]

            if basket_count == 0:
                print("Your basket is empty.")
            else:
                # Display the updated basket
                display_basket(shopper_id)

    conn.close()


def checkout(shopper_id):
    conn = sqlite3.connect('Shop_database.db')
    cursor = conn.cursor()

    # Check if the basket is empty
    cursor.execute("SELECT COUNT(*) "
                   "FROM basket_contents "
                   "WHERE basket_id = "
                   "(SELECT basket_id FROM shopper_baskets WHERE shopper_id = ?)", (shopper_id,))
    basket_count = cursor.fetchone()[0]

    if basket_count == 0:
        print("Your basket is empty.")
        conn.close()
        return

    # Display current basket and ask for confirmation
    display_basket(shopper_id)
    proceed = input("Do you wish to proceed with the checkout? (Y/N): ")
    if proceed.lower() != "y":
        conn.close()
        return

    try:
        # Insert a new row into the shopper_orders table
        order_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("INSERT INTO shopper_orders "
                       "(shopper_id, order_status, order_date) "
                       "VALUES (?, 'Placed', ?)", (shopper_id, order_date))

        # Get the order_id of the inserted row
        order_id = cursor.lastrowid

        # Insert a new row into the ordered_products table for each item in the basket
        cursor.execute("INSERT INTO ordered_products "
                       "(order_id, product_id, seller_id, price, quantity, ordered_product_status) "
                       "SELECT ?, product_id, seller_id, price, quantity, 'Placed' "
                       "FROM basket_contents WHERE basket_id = "
                       "(SELECT basket_id FROM shopper_baskets WHERE shopper_id = ?)",
                       (order_id, shopper_id))

        # Delete rows from shopper_baskets and basket_contents tables
        cursor.execute(
            "DELETE FROM basket_contents WHERE basket_id = "
            "(SELECT basket_id FROM shopper_baskets WHERE shopper_id = ?)",
            (shopper_id,))
        cursor.execute(
            "DELETE FROM shopper_baskets WHERE basket_id = "
            "(SELECT basket_id FROM shopper_baskets WHERE shopper_id = ?)",
            (shopper_id,))

        conn.commit()

        print("Checkout complete, your order has been placed.")
    except sqlite3.Error as e:
        print("An error occurred:", e)

    conn.close()


def exit_program():
    print("Exiting the program. Goodbye!")
    exit()
