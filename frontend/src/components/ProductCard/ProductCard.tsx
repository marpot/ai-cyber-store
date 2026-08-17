import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

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

  console.log("PRODUCT CARD IMAGE:", image);

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

    </article>
  );
}