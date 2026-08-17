import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";

import { useScroll } from "@/context/ScrollContext";
import { useCart } from "@/context/CartContext";

import "@/pages/Cart/Cart.scss";

export default function Cart() {
  const { t } = useTranslation();

  const navigate = useNavigate();

  const { scrollTo } = useScroll();

  const {
    cart,
    loading,
    updateQuantity,
    removeItem,
  } = useCart();

  const handleContinueShopping = () => {
    navigate("/");

    setTimeout(() => {
      scrollTo("shop");
    }, 100);
  };

  if (!cart || cart.items.length === 0) {
    return (
      <section className="cart-page">
        <div className="cart-page__content">

          <h1>
            {t("cart.title")}
          </h1>

          <p>
            {t("cart.empty")}
          </p>

          <button
            className="cart-page__back"
            type="button"
            onClick={handleContinueShopping}
          >
            ← {t("cart.continueShopping")}
          </button>

        </div>
      </section>
    );
  }

  const total =
    Number(cart.totals.total_price) / 100;

  return (
    <section className="cart-page">
      <div className="cart-page__content">

        <button
          className="cart-page__back"
          type="button"
          onClick={handleContinueShopping}
        >
          ← {t("cart.continueShopping")}
        </button>

        <h1>
          {t("cart.title")}
        </h1>

        <div className="cart-page__items">

          {cart.items.map((item) => {
            const price =
              Number(item.prices.price) / 100;

            return (
              <article
                className="cart-item"
                key={item.key}
              >

                {item.images?.[0]?.src && (
                  <div className="cart-item__image">
                    <img
                      src={item.images[0].src}
                      alt={
                        item.images[0].alt ||
                        item.name
                      }
                    />
                  </div>
                )}

                <div className="cart-item__info">

                  <h2>
                    {item.name}
                  </h2>

                  <span>
                    {price.toFixed(2)}{" "}
                    {item.prices.currency_symbol}
                  </span>

                </div>

                <div className="cart-item__quantity">

                  <button
                    type="button"
                    disabled={loading}
                    onClick={() =>
                      updateQuantity(
                        item.key,
                        item.quantity - 1
                      )
                    }
                  >
                    −
                  </button>

                  <span>
                    {item.quantity}
                  </span>

                  <button
                    type="button"
                    disabled={loading}
                    onClick={() =>
                      updateQuantity(
                        item.key,
                        item.quantity + 1
                      )
                    }
                  >
                    +
                  </button>

                </div>

                <button
                  className="cart-item__remove"
                  type="button"
                  disabled={loading}
                  onClick={() =>
                    removeItem(item.key)
                  }
                >
                  {t("cart.remove")}
                </button>

              </article>
            );
          })}

        </div>

        <div className="cart-page__summary">

          <span>
            {t("cart.total")}
          </span>

          <strong>
            {total.toFixed(2)}{" "}
            {cart.totals.currency_symbol}
          </strong>

        </div>

        <button
          className="cart-page__checkout"
          type="button"
          onClick={() => {
            console.log(
              "Checkout coming next"
            );
          }}
        >
          {t("cart.checkout")}
        </button>

      </div>
    </section>
  );
}