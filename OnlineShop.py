from menu_functions import *


def retrieve_shopper_id():
    conn = sqlite3.connect('Shop_database.db')
    c = conn.cursor()

    while True:
        shopper_id = input("Please enter your shopper ID: ")
        c.execute("SELECT * FROM shoppers WHERE shopper_id = ?",
                  (shopper_id,))
        result = c.fetchone()
        if result:
            return result
        else:
            print("Invalid shopper ID. Please try again.")


def retrieve_current_basket(shopper_id):
    conn = sqlite3.connect('Shop_database.db')
    c = conn.cursor()

    c.execute("""SELECT basket_id
                 FROM shopper_baskets
                 WHERE shopper_id = ?
                 AND DATE(basket_created_date_time) = DATE('now')
                 ORDER BY basket_created_date_time DESC
                 LIMIT 1""", (shopper_id,))
    result = c.fetchone()
    if result:
        return result[0]
    else:
        return None


def display_current_basket(basket_id):
    conn = sqlite3.connect('Shop_database.db')
    c = conn.cursor()

    c.execute("""SELECT p.product_description, bc.quantity, ps.price
                 FROM basket_contents bc
                 JOIN products p ON bc.product_id = p.product_id
                 JOIN product_sellers ps ON bc.product_id = ps.product_id AND bc.seller_id = ps.seller_id
                 WHERE bc.basket_id = ?""", (basket_id,))
    basket_items = c.fetchall()

    if basket_items:
        print("\nWelcome back. Your current basket has been loaded:\n")
        print("{:<70} {:<10} {:<10}".format("Product", "Quantity", "Price"))
        print("-" * 90)
        for item in basket_items:
            product_description = item[0]
            quantity = item[1]
            price = "£" + str(item[2])
            print("{:<70} {:<10} {:<10}".format(product_description, quantity, price))
        print("-" * 90)
    else:
        print("No items in the current basket.")


def main():
    shopper_info = retrieve_shopper_id()
    if shopper_info:
        shopper_first_name = shopper_info[2]
        shopper_id = shopper_info[0]
        current_basket_id = retrieve_current_basket(shopper_id)
        if current_basket_id:
            display_current_basket(current_basket_id)
        else:
            print("No items in the current basket.")
        main_menu(shopper_first_name, shopper_id)


if __name__ == "__main__":
    main()
