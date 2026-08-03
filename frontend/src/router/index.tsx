import { createBrowserRouter } from "react-router-dom";

import MainLayout from "@/layouts/MainLayout";

import Home from "@/pages/Home";
import Product from "@/pages/Product";


const router = createBrowserRouter([

  {
    path: "/",

    element: <MainLayout />,

    children: [

      {
        index: true,
        element: <Home />,
      },


      {
        path: "product/:id",
        element: <Product />,
      },

    ],

  },

]);


export default router;