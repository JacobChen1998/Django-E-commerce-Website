import os
from order_system.settings import BASE_DIR

PRODUCTS_FILE = os.path.join(BASE_DIR, 'products.txt')

def load_products_from_file():
    categories = {}
    current_category = None
    product_id = 1  # 初始化产品ID
    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            if line.startswith("'") and line.endswith("'"):
                current_category = line.strip("'")
                categories[current_category] = []
            elif current_category and line.startswith('-'):
                parts = line[1:].strip().split()
                name = parts[0]
                image = parts[1]
                price = float(parts[2])
                quantity = int(parts[3])
                description = parts[4]
                categories[current_category].append({
                    'id': product_id,  # 分配唯一的产品ID
                    'name': name,
                    'image': image,
                    'price': price,
                    'quantity': quantity,
                    'description':description,
                })
                print(categories[current_category][-1])
                product_id += 1  # 增加产品ID
    return categories


def save_products_to_file(categories):
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as file:
        for category, products in categories.items():
            file.write(f"'{category}'\n")
            for product in products:
                file.write(f"    - {product['name']} {product['image']} {product['price']} {product['quantity']}\n")
