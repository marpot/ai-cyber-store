import {
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  useTranslation,
} from "react-i18next";

import {
  useScroll,
} from "@/context/ScrollContext";

import {
  useCart,
} from "@/context/CartContext";

import "./Product.scss";

interface ProductData {
  id: number;

  name: string;

  description: string;

  prices: {
    price: string;
    regular_price: string;
    sale_price: string;
    currency_symbol: string;
  };

  images: {
    src: string;
    alt: string;
  }[];

  is_on_sale: boolean;

  is_purchasable: boolean;

  is_in_stock: boolean;
}

export default function Product() {
  const { id } =
    useParams<{
      id: string;
    }>();

  const { t } =
    useTranslation();

  const navigate =
    useNavigate();

  const { scrollTo } =
    useScroll();

  const {
    addToCart,
    loading: cartLoading,
  } = useCart();

  const API_URL =
    import.meta.env
      .VITE_WP_API_URL;

  const [product, setProduct] =
    useState<ProductData | null>(
      null
    );

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(
      null
    );

  /*
   * Powrót do sklepu.
   */

  const handleBack = () => {
    navigate("/");

    setTimeout(() => {
      scrollTo("shop");
    }, 100);
  };

  /*
   * Pobranie produktu
   * z WooCommerce Store API.
   */

  useEffect(() => {
    if (!id) {
      setError(
        t("product.missingId")
      );

      setLoading(false);

      return;
    }

    const url =
      `${API_URL}/wp-json/wc/store/v1/products/${id}`;

    console.log(
      "========== PRODUCT DEBUG =========="
    );

    console.log(
      "Product ID:",
      id
    );

    console.log(
      "API URL:",
      API_URL
    );

    console.log(
      "Request URL:",
      url
    );

    setLoading(true);

    setError(null);

    fetch(url)
      .then(async (response) => {
        console.log(
          "HTTP status:",
          response.status
        );

        console.log(
          "HTTP OK:",
          response.ok
        );

        if (!response.ok) {
          const text =
            await response.text();

          console.error(
            "WooCommerce response:",
            text
          );

          throw new Error(
            `WooCommerce HTTP ${response.status}`
          );
        }

        const data =
          await response.json();

        console.log(
          "WooCommerce product:",
          data
        );

        return data;
      })

      .then(
        (data: ProductData) => {
          setProduct(data);

          setLoading(false);
        }
      )

      .catch(
        (err: Error) => {
          console.error(
            "WooCommerce product error:",
            err
          );

          setError(
            err.message
          );

          setLoading(false);
        }
      );
  }, [
    API_URL,
    id,
    t,
  ]);

  /*
   * Stan ładowania.
   */

  if (loading) {
    return (
      <section className="product-page">
        <button
          className="product-page__back"
          onClick={handleBack}
        >
          ←{" "}
          {t(
            "product.back"
          )}
        </button>

        <div className="product-page__content">
          <h1>
            {t(
              "shop.loading"
            )}
          </h1>
        </div>
      </section>
    );
  }

  /*
   * Błąd / brak produktu.
   */

  if (
    error ||
    !product
  ) {
    return (
      <section className="product-page">
        <button
          className="product-page__back"
          onClick={handleBack}
        >
          ←{" "}
          {t(
            "product.back"
          )}
        </button>

        <div className="product-page__content">
          <h1>
            {t(
              "product.notFound"
            )}
          </h1>

          <p>
            {error ||
              t(
                "product.fetchError"
              )}
          </p>

          <p>
            {t(
              "product.productId"
            )}
            : {id}
          </p>

          <p>
            {t(
              "product.api"
            )}
            : {API_URL}
          </p>
        </div>
      </section>
    );
  }

  /*
   * Ceny WooCommerce są zwracane
   * w najmniejszej jednostce waluty.
   *
   * 3900 = 39.00 PLN
   */

  const price =
    Number(
      product.prices.price
    ) / 100;

  const regularPrice =
    Number(
      product.prices
        .regular_price
    ) / 100;

  /*
   * Widok produktu.
   */

  return (
    <section className="product-page">
      <button
        className="product-page__back"
        onClick={handleBack}
      >
        ←{" "}
        {t(
          "product.back"
        )}
      </button>

      <div className="product-page__content">

        {product.images?.[0]?.src && (
          <div className="product-page__image">
            <img
              src={
                product.images[0].src
              }
              alt={
                product.images[0].alt ||
                product.name
              }
            />
          </div>
        )}

        <h1>
          {product.name}
        </h1>

        <div
          className="product-page__description"
          dangerouslySetInnerHTML={{
            __html:
              product.description,
          }}
        />

        <div className="product-page__price">

          {product.is_on_sale && (
            <span className="product-page__regular-price">
              {regularPrice.toFixed(
                2
              )}{" "}
              {
                product.prices
                  .currency_symbol
              }
            </span>
          )}

          <span>
            {price.toFixed(
              2
            )}{" "}
            {
              product.prices
                .currency_symbol
            }
          </span>

        </div>

        {product.is_in_stock &&
          product.is_purchasable && (
            <button
              className="product-page__cart"
              type="button"
              disabled={
                cartLoading
              }
              onClick={async () => {
                try {
                  console.log(
                    "Adding WooCommerce product:",
                    product.id
                  );

                  await addToCart(
                    product.id
                  );

                  navigate(
                    "/cart"
                  );
                } catch (error) {
                  console.error(
                    "Could not add product to cart:",
                    error
                  );
                }
              }}
            >
              {cartLoading
                ? t(
                    "cart.adding"
                  )
                : t(
                    "product.addToCart"
                  )}
            </button>
          )}

      </div>
    </section>
  );
}