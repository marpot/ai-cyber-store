import "./ProductCard.scss";

interface ProductCardProps {
  name: string;
  description: string;
  price: string;
}

export default function ProductCard({
  name,
  description,
  price,
}: ProductCardProps) {
  return (
    <article className="product-card">
      <h3>{name}</h3>

      <p>
        {description}
      </p>

      <div className="product-card__footer">
        <span>
          {price}
        </span>

        <button>
          View
        </button>
      </div>
    </article>
  );
}