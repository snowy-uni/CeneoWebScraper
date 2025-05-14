from app.utils import extract


class Review:
    review_scheme = {
        "review_id": (None, "data-entry-id"),
        "author": (".user-post__author-name",),
        "content": (".user-post__text",),
        "score": (".user-post__score .user-post__score-count",),
        "recomendation": (".user-post__author-recomendation > em",),
        "pros": (".review-feature__item.review-feature__item--positive", None, True),
        "cons": (".review-feature__item.review-feature__item--negative", None, True),
        "likes": (".vote-yes > span",),
        "dislikes": (".vote-no > span",),
        "publish_date": (".user-post__published time:nth-of-type(1)", "datetime"),
        "purchase_date": (".user-post__published time:nth-of-type(2)", "datetime"),
    }

    def __init__(
        self,
        review_id="",
        author="",
        content="",
        score=0.0,
        recomendation="",
        pros=[],
        cons=[],
        likes=0,
        dislikes=0,
        publish_date="",
        purchase_date="",
    ):
        self.review_id = review_id
        self.author = author
        self.content = content
        self.score = score
        self.recomendation = recomendation
        self.pros = pros
        self.cons = cons
        self.likes = likes
        self.dislikes = dislikes
        self.publish_date = publish_date
        self.purchase_date = purchase_date

    def __str__(self):
        return "/n".join(
            [
                f"{feature}: {getattr(self, feature)}"
                for feature in self.review_scheme.keys()
            ]
        )

    def to_dict(self):
        return {
            feature: {getattr(self, feature)} for feature in self.review_scheme.keys()
        }

    def extract_features(self, review_raw):
        for key, value in self.review_scheme.items():
            setattr(self, key, extract(review_raw, *value))
        return self

    def transform(self):
        self.stars = float(self.stars.split("/")[0].replace(",", "."))
        self.likes = int(self.likes)
        self.dislikes = int(self.dislikes)
        # self.content = self.content.replace('\n', ' ')
        return self
