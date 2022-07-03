from tortoise.queryset import QuerySet


async def seed_data():
    from .models import Product

    models: QuerySet[Product] = Product.all() 
    count = await models.count() 
    
    if count == 0:
        mock_products = [
            Product(name="dell", price=2578.00),
            Product(name="hp", price=8937.00),
            Product(name="mac", price=5345.00), 
            Product(name="lenovo", price=1235.00), 
            Product(name="acer", price=1827.00)
        ]

        await Product.bulk_create(mock_products)
