from wtforms import Form, StringField, SubmitField, validators


class ProductForm(Form):
    product_id = StringField(
        "Kod produktu",
        name="product_id",
        id="product_id",
        validators=[
            validators.DataRequired(message="Kod jest wymagany"),
            validators.Regexp("^[0-9]*$", message="Kod musi się składać tylko z liczb"),
            validators.length(
                min=5, max=10, message="Kod produkty pomienien mieć od 5 do 10 cyfr"
            ),
        ],
    )
    submit = SubmitField("Pobierz opinie")
