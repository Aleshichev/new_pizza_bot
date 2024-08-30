CAPTION_1="<strong>{product.name}\
                </strong>\n{product.description}\nКоштує: {round(product.price, 2)}\n\
                <strong>Товар {paginator.page} з {paginator.pages}</strong>"



CAPTION_2="Товар: <strong>{cart.product.name}</strong>\
            \nВартість: <strong>{cart.product.price}</strong> грн\
            \nКількість: <strong>{cart.quantity}</strong> од.\
            \n\n------------------- Кошик ---------------------\
            \nУ вашему заказі <strong>{paginator.pages}</strong> товарів\
            \nВартість усього замовлення <strong>{total_price}</strong> грн"