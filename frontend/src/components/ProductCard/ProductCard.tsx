import { Link } from "react-router-dom";

import "./ProductCard.scss";


interface ProductCardProps {
  id: number;
  name: string;
  description: string;
  price: string;
}


export default function ProductCard({
  id,
  name,
  description,
  price,
}: ProductCardProps) {

  return (

    <article className="product-card">

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
          View
        </Link>


      </div>


    </article>

  );

}