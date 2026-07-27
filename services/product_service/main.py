from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Product Microservice",
    version="1.0.0"
)

PRODUCTS_DB = [
    {"id": "101", "name": "MacBook Pro M3", "price": 1999.99, "category": "Electronics"},
    {"id": "102", "name": "iPhone 15 Pro", "price": 999.99, "category": "Electronics"},
    {"id": "103", "name": "Mechanical Keyboard", "price": 149.99, "category": "Accessories"},
]


@app.get("/")
@app.get("/health")
def health():
    return {"service": "Product Service", "status": "healthy"}


@app.get("/products")
def get_products():
    return {
        "service": "Product Service",
        "count": len(PRODUCTS_DB),
        "products": PRODUCTS_DB
    }


@app.get("/products/{product_id}")
def get_product_by_id(product_id: str):
    product = next((p for p in PRODUCTS_DB if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"service": "Product Service", "product": product}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
