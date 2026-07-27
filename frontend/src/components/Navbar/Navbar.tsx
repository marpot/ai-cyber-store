import { NavLink } from "react-router-dom";
import "./Navbar.scss";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar__logo">
        AI Cyber Store
      </div>

      <div className="navbar__links">
        <NavLink to="/" end>
          Home
        </NavLink>

        <NavLink to="/shop">
          Shop
        </NavLink>

        <NavLink to="/cart">
          Cart
        </NavLink>
      </div>
    </nav>
  );
}

export default Navbar;