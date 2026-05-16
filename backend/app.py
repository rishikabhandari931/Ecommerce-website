from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import glob

app = Flask(__name__)
CORS(app)

# In-code dictionary for "dictionary (no CSV)" mode.
# Keyed by filename without extension (e.g., "images", "Chrysanthemum-Combo-Pack").
PRODUCT_DICTIONARY = {
    "Chrysanthemum-Combo-Pack": {
        "name": "Chrysanthemum Combo Pack",
        "description": "A vibrant mix of chrysanthemum varieties for bold seasonal color.",
        "price": 129,
    },
    "images": {
        "name": "LEXRX Face Cream",
        "description": "Hydration + glow for daily skincare.",
        "price": 300,
    },
    "nurserylive-flowering-plants-category-image-505581_600x600": {
        "name": "FujiFilm DSLR Camera",
        "description": "Capture sharp photos with adjustable settings.",
        "price": 35000,
    },
    "vastu-plants-april-month-sale-2026-banner-m-greenkin": {
        "name": "Sky Blue KIds Shoe",
        "description": "Comfort fit for everyday adventures.",
        "price": 910,
    },
    "WhatsApp-Image-2022-07-12-at-10.51.57-PM-5": {
        "name": "Vibrant Plant Bundle",
        "description": "A curated bundle of fresh greenery for your home.",
        "price": 499,
    },
}


def filename_stem(path_or_name: str) -> str:
    base = os.path.basename(path_or_name)
    stem, _ext = os.path.splitext(base)
    return stem


def title_from_stem(stem: str) -> str:
    cleaned = stem.replace("-", " ").replace("_", " ").strip()
    return " ".join([w.capitalize() for w in cleaned.split() if w])


def generate_products():
    # images/ folder is at repo root: ./images
    images_dir = os.path.join(os.getcwd(), "images")
    pattern = os.path.join(images_dir, "*")

    files = []
    for p in glob.glob(pattern):
        if os.path.isfile(p):
            files.append(p)

    # Deterministic ordering
    files.sort(key=lambda x: os.path.basename(x).lower())

    products_out = []
    next_id = 1
    for file_path in files:
        stem = filename_stem(file_path)
        file_name = os.path.basename(file_path)

        image_path = f"/images/{file_name}"
        dict_entry = PRODUCT_DICTIONARY.get(stem)

        if dict_entry:
            name = dict_entry.get("name", title_from_stem(stem))
            description = dict_entry.get("description", "")
            price = dict_entry.get("price", 0)
        else:
            name = title_from_stem(stem)
            description = "Product details coming soon."
            price = 0

        products_out.append(
            {
                "id": next_id,
                "name": name,
                "description": description,
                "image": image_path,
                "price": price,
            }
        )
        next_id += 1

    return products_out


# We generate products at startup.
products = generate_products()


@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(products)


@app.route("/products", methods=["POST"])
def add_product():
    data = request.json or {}
    # Keep ids unique within the current in-memory list.
    next_id = (max((p["id"] for p in products), default=0) + 1) if products else 1
    data["id"] = next_id
    products.append(data)
    return jsonify({"message": "Product added"})


@app.route("/buy/<int:id>", methods=["POST"])
def buy(id):
    return jsonify({"message": f"Product {id} purchased"})


if __name__ == "__main__":
    app.run(debug=True)
