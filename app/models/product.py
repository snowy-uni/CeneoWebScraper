import json
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from config import headers
from app.utils import extract

from app.models.review import Review


class Product:
    def __init__(self, product_id, reviews=[], product_name="", stats={}):
        self.product_id = product_id
        self.reviews = reviews
        self.product_name = product_name
        self.stats = stats

    def __str__(self):
        return f"""
            product_id: {self.product_id}
            product_name: {json.dumps(self.stats, indent=4, ensure_ascii=False)}
            reviews: {'\n\n'.join(str(review) for review in self.reviews)}
        """

    def reviews_to_dict(self):
        return [review.to_dict() for review in self.reviews]

    def info_to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "stats": self.stats,
        }

    def extract_product_name(self):
        next_page = f"https://www.ceneo.pl/{self.product_id}#tab=reviews"
        res = requests.get(next_page, headers=headers)
        if res.status_code == 200:
            page_dom = BeautifulSoup(res.text, "html.parser")
            self.product_name = extract(page_dom, "h1")
        else:
            self.product_name = ""
        return self

    def extract_reviews(self):
        next_page = f"https://www.ceneo.pl/{self.product_id}#tab=reviews"
        while next_page:
            res = requests.get(next_page, headers=headers)
            print(res.status_code)
            print(next_page)
            if res.status_code == 200:

                page_dom = BeautifulSoup(res.text, "html.parser")
                reviews = page_dom.select(
                    "div.js_product-review:not(.user-post--highlight)"
                )

                for review in reviews:
                    single_review = Review()
                    self.reviews.append(
                        single_review.extract_features(review).transform()
                    )

                try:
                    next_page = "https://www.ceneo.pl" + extract(
                        page_dom, ".pagination__next", "href"
                    )
                except TypeError:
                    next_page = None
        return self

    def calc_stats(self):
        reviews = pd.DataFrame.from_dict(self.reviews_to_dict())
        self.stats["reviews_count"] = reviews.shape[0]
        self.stats["pros_count"] = reviews.pros.astype(bool).sum()
        self.stats["cons_count"] = reviews.cons.astype(bool).sum()
        self.stats["pros_cons_count"] = reviews.apply(
            lambda r: bool(r.pros) and bool(r.cons), axis=1
        ).sum()
        self.stats["average_score"] = round(reviews.score.mean(), 2)
        return self

    def export_reviews(self):
        if not os.path.exists(".app/data/opinions"):
            os.mkdir(".app/data/opinions")
        with open(
            f".app/data/opinions/{self.product_id}.json", "w", encoding="UTF-8"
        ) as file:
            json.dump(self.reviews_to_dict(), file, indent=4, ensure_ascii=False)

    def export_info(self):
        if not os.path.exists(".app/data/products"):
            os.mkdir(".app/data/products")
        with open(
            f".app/data/products/{self.product_id}.json", "w", encoding="UTF-8"
        ) as file:
            json.dump(self.reviews_to_dict(), file, indent=4, ensure_ascii=False)
