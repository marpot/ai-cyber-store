import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

interface CartImage {
  src: string;
  alt: string;
}

export interface CartItem {
  key: string;
  id: number;
  quantity: number;
  name: string;
  prices: {
    price: string;
    currency_code: string;
    currency_symbol: string;
  };
  images: CartImage[];
}

interface CartData {
  items: CartItem[];
  totals: {
    total_items: string;
    total_price: string;
    currency_code: string;
    currency_symbol: string;
  };
}

interface CartContextType {
  cart: CartData | null;
  loading: boolean;

  addToCart: (
    productId: number,
    quantity?: number
  ) => Promise<void>;

  updateQuantity: (
    key: string,
    quantity: number
  ) => Promise<void>;

  removeItem: (
    key: string
  ) => Promise<void>;

  refreshCart: () => Promise<void>;
}

const CartContext =
  createContext<CartContextType | undefined>(undefined);

export function CartProvider({
  children,
}: {
  children: ReactNode;
}) {
  const API_URL = import.meta.env.VITE_WP_API_URL;

  const [cart, setCart] =
    useState<CartData | null>(null);

  const [loading, setLoading] =
    useState(false);

  /*
   * WooCommerce Store API
   *
   * Cart-Token:
   * identyfikuje koszyk konkretnego klienta.
   *
   * Nonce:
   * wymagany przez WooCommerce przy operacjach
   * POST modyfikujących koszyk.
   */

  const getCartToken = () => {
    return sessionStorage.getItem(
      "wc_cart_token"
    );
  };

  const saveCartToken = (
    token: string | null
  ) => {
    if (token) {
      sessionStorage.setItem(
        "wc_cart_token",
        token
      );
    }
  };

  const getNonce = () => {
    return sessionStorage.getItem(
      "wc_cart_nonce"
    );
  };

  const saveNonce = (
    nonce: string | null
  ) => {
    if (nonce) {
      sessionStorage.setItem(
        "wc_cart_nonce",
        nonce
      );
    }
  };

  /*
   * Wspólna funkcja do komunikacji
   * z WooCommerce Store API.
   */

  const request = async (
    endpoint: string,
    options: RequestInit = {}
  ) => {
    const cartToken =
      getCartToken();

    const nonce =
      getNonce();

    const headers =
      new Headers(options.headers);

    headers.set(
      "Content-Type",
      "application/json"
    );

    if (cartToken) {
      headers.set(
        "Cart-Token",
        cartToken
      );
    }

    if (nonce) {
      headers.set(
        "Nonce",
        nonce
      );
    }

    console.log(
      "WooCommerce request:",
      {
        endpoint,
        method:
          options.method || "GET",
        cartToken: !!cartToken,
        nonce: nonce || null,
      }
    );

    const response =
      await fetch(
        `${API_URL}/wp-json/wc/store/v1/cart${endpoint}`,
        {
          ...options,
          headers,
          credentials: "include",
        }
      );

    /*
     * WooCommerce może zwrócić
     * nowy Cart-Token.
     */

    const newCartToken =
      response.headers.get(
        "Cart-Token"
      );

    /*
     * WooCommerce zwraca również Nonce.
     */

    const newNonce =
      response.headers.get(
        "Nonce"
      );

    console.log(
      "WooCommerce response headers:",
      {
        cartToken:
          newCartToken,
        nonce:
          newNonce,
      }
    );

    saveCartToken(
      newCartToken
    );

    saveNonce(
      newNonce
    );

    if (!response.ok) {
      const errorText =
        await response.text();

      throw new Error(
        `WooCommerce Cart API ${response.status}: ${errorText}`
      );
    }

    return response.json();
  };

  /*
   * Pobranie aktualnego koszyka.
   *
   * GET /cart
   *
   * Ten request również inicjalizuje
   * Cart-Token oraz Nonce.
   */

  const refreshCart =
    useCallback(async () => {
      try {
        setLoading(true);

        const data =
          await request("");

        setCart(data);
      } catch (error) {
        console.error(
          "Cart loading error:",
          error
        );
      } finally {
        setLoading(false);
      }
    }, [API_URL]);

  /*
   * Dodawanie produktu.
   *
   * WooCommerce wymaga Nonce przy POST.
   *
   * Jeżeli aplikacja jeszcze go nie posiada,
   * najpierw pobieramy /cart.
   */

  const addToCart = async (
    productId: number,
    quantity = 1
  ) => {
    try {
      setLoading(true);

      if (!getNonce()) {
        console.log(
          "No WooCommerce nonce found. Initializing cart..."
        );

        await request("");
      }

      console.log(
        "Adding product to cart:",
        {
          productId,
          quantity,
          nonce:
            getNonce(),
          cartToken:
            getCartToken(),
        }
      );

      const data =
        await request(
          `/add-item?id=${productId}&quantity=${quantity}`,
          {
            method: "POST",
          }
        );

      setCart(data);
    } catch (error) {
      console.error(
        "Add to cart error:",
        error
      );

      throw error;
    } finally {
      setLoading(false);
    }
  };

  /*
   * Zmiana ilości produktu.
   */

  const updateQuantity =
    async (
      key: string,
      quantity: number
    ) => {
      if (quantity <= 0) {
        await removeItem(key);
        return;
      }

      try {
        setLoading(true);

        if (!getNonce()) {
          await request("");
        }

        const data =
          await request(
            `/update-item?key=${encodeURIComponent(
              key
            )}&quantity=${quantity}`,
            {
              method: "POST",
            }
          );

        setCart(data);
      } catch (error) {
        console.error(
          "Update cart error:",
          error
        );

        throw error;
      } finally {
        setLoading(false);
      }
    };

  /*
   * Usunięcie produktu z koszyka.
   */

  const removeItem =
    async (
      key: string
    ) => {
      try {
        setLoading(true);

        if (!getNonce()) {
          await request("");
        }

        const data =
          await request(
            `/remove-item?key=${encodeURIComponent(
              key
            )}`,
            {
              method: "POST",
            }
          );

        setCart(data);
      } catch (error) {
        console.error(
          "Remove cart error:",
          error
        );

        throw error;
      } finally {
        setLoading(false);
      }
    };

  /*
   * Inicjalizacja koszyka
   * po uruchomieniu aplikacji.
   */

  useEffect(() => {
    refreshCart();
  }, [refreshCart]);

  return (
    <CartContext.Provider
      value={{
        cart,
        loading,
        addToCart,
        updateQuantity,
        removeItem,
        refreshCart,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context =
    useContext(CartContext);

  if (!context) {
    throw new Error(
      "useCart must be used inside CartProvider"
    );
  }

  return context;
}