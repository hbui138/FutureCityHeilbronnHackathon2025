# FutureCityHeilbronnHackathon2025

/data
  ├── stores.json
  ├── products.json
  └── store_products.json

## 1️. `store.json` – Store Master Data

Contains details about stores, their location, opening hours, and rating.

```json
{
  "stores": [
    {
      "store_id": string,
      "store_name": string,
      "location": {
        "address": string,
        "city": string,
        "state": string,
        "latitude": float [-90, 90],
        "longitude": float [-180, 180]
      },
      "opening_hours": {
        "Monday": { "open": "HH:MM", "close": "HH:MM" },
        "Tuesday": { "open": "HH:MM", "close": "HH:MM" },
        "Wednesday": { "open": "HH:MM", "close": "HH:MM" },
        "Thursday": { "open": "HH:MM", "close": "HH:MM" },
        "Friday": { "open": "HH:MM", "close": "HH:MM" },
        "Saturday": { "open": "HH:MM", "close": "HH:MM" },
        "Sunday": { "open": "HH:MM", "close": "HH:MM" }
      },
      "store_rating": float [0, 5]
    }
  ]
}
```

## Field Descriptions

- **store_id**: Unique identifier for the store.  
- **store_name**: Name of the store.  
- **location**: Object containing `address`, `city`, `state`, `latitude`, and `longitude`.  
- **opening_hours**: Object containing daily opening times.  
  Each day of the week (`Monday`, `Tuesday`, … `Sunday`) is an object with:  
  - **open**: Opening time in `HH:MM` format.  
  - **close**: Closing time in `HH:MM` format.  
- **store_rating**: Average rating of the store.  

## ️2. `store.json` – Store Master Data

Contains information about products, their brand, category, packaging.

```json
{
  "products": [
    {
      "product_id": string,
      "product_name": string,
      "brand": string,
      "category": string,
      "subcategory": string,
      "package": {
        "weight": float,
        "weight_unit": string,
        "package_type": string
      },
    }
  ]
}
```

## Field Descriptions

- **product_id**: Unique product identifier.  
- **product_name**: Name of the product.  
- **brand**: Product brand.  
- **category / subcategory**: Classification of product.  
- **package**: Object describing the product packaging:  
  - **weight**: Numeric value of weight.  
  - **weight_unit**: Unit of weight (e.g., L, kg). 
  - **package_type**: Type of package (e.g., carton, bottle).

## 3. store_products.json – Inventory & Pricing per Store

Contains store-specific inventory, pricing.

```json
{
  "store_products": [
    {
      "store_id": string,
      "product_id": string,
      "pricing": {
        "normal_price": float,
        "real_price": float (= "normal_price" x (1 - "discount_percentage"),
        "discount_percentage": float [0, 100]
      },
      "stock_info": {
        "stock": int (>= 0),
        "availability_status": int [0, 5],
        "restock_date": datetime
      },
    }
  ]
}
```

## Field Descriptions

- **store_id**: Identifier linking to `store.json`.  
- **product_id**: Identifier linking to `products.json`.  
- **pricing**: Object containing:  
  - **normal_price**: Regular price of the product.  
  - **real_price**: Current price after discount.  
  - **discount_percentage**: Discount applied on normal price.
- **stock_info**: Object containing:  
  - **stock**: Number of units available.  
  - **availability_status**: (number from 0 to 5 denotes the status, 5 being high stocks and 0 being out of stocks).  
  - **restock_date**: Next expected restock date.  





