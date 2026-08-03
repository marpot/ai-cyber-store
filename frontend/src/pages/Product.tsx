import { useParams } from "react-router-dom";


export default function Product() {

  const { id } = useParams();


  return (
    <div>

      <h1>
        Product
      </h1>


      <p>
        ID: {id}
      </p>


    </div>
  );
}