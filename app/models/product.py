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

    def reviews_from_dict(self, reviews_list):
        for review_dict in reviews_list:
            review = Review()
            review.from_dict()
            self.reviews.append(review)

    def info_to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "stats": self.stats,
        }

    def info_from_dict(self, info):
        self.product_id = info["product_id"]
        self.product_name = info["product_name"]
        self.stats = info["stats"]

    def if_not_exists(self):
        next_page = f"https://www.ceneo.pl/{self.product_id}#tab=reviews"
        res = requests.get(next_page, headers=headers)
        if res.status_code == 200:
            page_dom = BeautifulSoup(res.text, "html.parser")
            opinions_count = extract(page_dom, "a.product-review__link > span")
            if opinions_count:
                return False
            else:
                return "Dla produktu o podanym kodzie nie ma jeszcze opinii"
        else:
            return "Produkt o podanym kodzie nie istnieje"

    def extract_name(self):
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
            else:
                next_page = None
        return self

    def calc_stats(self):
        reviews = pd.DataFrame.from_dict(self.reviews_to_dict())
        print(reviews.pros)
        self.stats["reviews_count"] = int(reviews.shape[0])
        self.stats["pros_count"] = int(reviews.pros.astype(bool).sum())
        self.stats["cons_count"] = int(reviews.cons.astype(bool).sum())
        self.stats["pros_cons_count"] = int(
            reviews.apply(lambda r: bool(r.pros) and bool(r.cons), axis=1).sum()
        )
        self.stats["average_score"] = float(round(reviews.score.mean(), 2))
        print(self.stats)
        return self

    def export_reviews(self):
        if not os.path.exists("./app/data"):
            os.mkdir("./app/data")
        if not os.path.exists("./app/data/opinions"):
            os.mkdir("./app/data/opinions")
        with open(
            f"./app/data/opinions/{self.product_id}.json", "w", encoding="UTF-8"
        ) as file:
            json.dump(self.reviews_to_dict(), file, indent=4, ensure_ascii=False)

    def export_info(self):
        if not os.path.exists("./app/data"):
            os.mkdir("./app/data")
        if not os.path.exists("./app/data/products"):
            os.mkdir("./app/data/products")
        with open(
            f"./app/data/products/{self.product_id}.json", "w", encoding="UTF-8"
        ) as file:
            json.dump(self.info_to_dict(), file, indent=4, ensure_ascii=False)
