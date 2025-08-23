from django.core.management.base import BaseCommand
from products.models import Category, ColorVariant, SizeVariant, Product, ProductImage
from django.core.files.base import ContentFile
import requests
from io import BytesIO

class Command(BaseCommand):
    help = "Populate the database with sample clothing products"

    def handle(self, *args, **kwargs):
        # 1. Create Category
        category, _ = Category.objects.get_or_create(
            category_name="Clothing",
            defaults={"category_image": "categories/clothing.jpg"}
        )

        # 2. Create Color Variants
        colors = [
            {"name": "Red", "price": 0},
            {"name": "Blue", "price": 50},
            {"name": "Black", "price": 100}
        ]
        color_objs = []
        for c in colors:
            obj, _ = ColorVariant.objects.get_or_create(color_name=c["name"], price=c["price"])
            color_objs.append(obj)

        # 3. Create Size Variants
        sizes = [
            {"name": "Small", "price": 0, "order": 1},
            {"name": "Medium", "price": 50, "order": 2},
            {"name": "Large", "price": 100, "order": 3}
        ]
        size_objs = []
        for s in sizes:
            obj, _ = SizeVariant.objects.get_or_create(size_name=s["name"], price=s["price"], order=s["order"])
            size_objs.append(obj)

        # 4. Create Products
        products = [
            {
                "name": "crop orange T-Shirt",
                "price": 2000,
                "description": "A comfortable and stylish orange t-shirt perfect for everyday wear.",
                "image_url": "https://images.unsplash.com/photo-1625072651838-2a69ff8ed257?w=400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTZ8fGZhc2hpb24lMjBjbG90aGluZ3xlbnwwfHwwfHx8MA%3D%3D"
            },
            {
                "name": "Yello gay Jacket",
                "price": 5000,
                "description": "A classic yello denim jacket, great for casual outings.",
                "image_url": "https://plus.unsplash.com/premium_photo-1681433602478-dc69b2b49153?w=400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTd8fGZhc2hpb24lMjBjbG90aGluZ3xlbnwwfHwwfHx8MA%3D%3D"
            },
            {
                "name": "hot Jackets",
                "price": 3500,
                "description": "A warm and cozy jackets for chilly days.",
                "image_url": "https://images.unsplash.com/photo-1590033951631-a3b5dc4d368f?w=400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjB8fGZhc2hpb24lMjBjbG90aGluZ3xlbnwwfHwwfHx8MA%3D%3D"
            }
        ]

        for p in products:
            product, created = Product.objects.get_or_create(
                product_name=p["name"],
                category=category,
                defaults={
                    "price": p["price"],
                    "product_desription": p["description"],
                    "newest_product": True
                }
            )

            if created:
                product.color_variant.set(color_objs)
                product.size_variant.set(size_objs)

                # Download and attach product image
                response = requests.get(p["image_url"])
                if response.status_code == 200:
                    img_content = ContentFile(response.content)
                    img_obj = ProductImage(product=product)
                    img_obj.image.save(f"{p['name'].replace(' ', '_')}.png", img_content, save=True)

        self.stdout.write(self.style.SUCCESS("✅ Sample clothing products added successfully!"))
