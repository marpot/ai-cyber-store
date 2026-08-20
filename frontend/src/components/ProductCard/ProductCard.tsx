import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { useCart } from "@/context/CartContext";

import "./ProductCard.scss";

interface ProductCardProps {
  id: number;
  name: string;
  description: string;
  price: string;
  image?: string;
  isOnSale?: boolean;
}

export default function ProductCard({
  id,
  name,
  description,
  price,
  image,
  isOnSale,
}: ProductCardProps) {
  const { t } = useTranslation();

  const { addToCart, loading } = useCart();

  const [added, setAdded] = useState(false);

  const handleAddToCart = async () => {
    try {
      await addToCart(id);

      setAdded(true);

      setTimeout(() => {
        setAdded(false);
      }, 3000);
    } catch (error) {
      console.error(
        "Failed to add product to cart:",
        error
      );
    }
  };

  return (
    <article className="product-card">

      {image && (
        <div className="product-card__image">
          <img
            src={image}
            alt={name}
          />
        </div>
      )}

      {isOnSale && (
        <span className="product-card__badge">
          SALE
        </span>
      )}

      <h3>
        {name}
      </h3>

      <p>
        {description}
      </p>

      <div className="product-card__footer">

        <span>
          {price}
        </span>

        <Link
          to={`/product/${id}`}
          className="product-card__button"
        >
          {t("shop.view")}
        </Link>

      </div>

      <button
        type="button"
        className="product-card__cart"
        disabled={loading}
        onClick={handleAddToCart}
      >
        {loading
          ? t("cart.adding")
          : t("cart.addToCart")}
      </button>

      {added && (
        <div className="product-card__notification">
          <span>
            ✓
          </span>

          <span>
            {t("cart.added")}
          </span>

          <Link to="/cart">
            {t("cart.goToCart")}
          </Link>
        </div>
      )}

    </article>
  );
}