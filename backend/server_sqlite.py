# This file shows the key changes needed for SQLite
# Will be merged into server.py

# At startup, initialize database
@app.on_event("startup")
async def startup_event():
    await db.init_db()
    logging.info("SQLite database initialized")

# Example conversions:

# MongoDB: await db.products.find({"active": True}).to_list(100)
# SQLite: await db.find_many("products", {"active": 1}, limit=100)

# MongoDB: await db.products.insert_one(data)
# SQLite: await db.insert_one("products", data)

# MongoDB: await db.products.find_one({"product_id": id})
# SQLite: await db.find_one("products", {"product_id": id})

# MongoDB: await db.products.update_one({"product_id": id}, {"$set": data})
# SQLite: await db.update_one("products", {"product_id": id}, data)

# MongoDB: await db.products.delete_one({"product_id": id})
# SQLite: deleted_count = await db.delete_one("products", {"product_id": id})

# For lists/dicts in SQLite, need to serialize:
# Before insert: data["colors"] = db.serialize_list(data["colors"])
# After fetch: data["colors"] = db.deserialize_list(data["colors"])
