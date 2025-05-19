import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../style.css";

function NavBar({ onSearch }) {
  const [query, setQuery] = useState("");
  const [menuOpen, setMenuOpen] = useState(false); // state to toggle the menu
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/search?q=${query}`);
    }
  };

  const toggleMenu = () => {
    setMenuOpen(!menuOpen); // Toggle menu visibility
  };

  return (
    <nav className='navbar'>
      <div className='content'>
        <div className='logoContainer'>
          <Link to="/">
            <span className='logo'><strong>F1 News</strong></span>
          </Link>
        </div>

        <div 
          className={`hamburger ${menuOpen ? "open" : ""}`}
          onClick={toggleMenu}
        >
          <span></span>
          <span></span>
          <span></span>
        </div>

        <div className={`links ${menuOpen ? "open" : ""}`}>
          <Link to="/about">
            <span className='link'>About</span>
          </Link>
          <form onSubmit={handleSearch} className='form'>
            <input
              type="text"
              placeholder="請用英文名稱搜尋"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className='input'
            />
            <button type="submit" className='button'>搜尋</button>
          </form>
        </div>
      </div>
    </nav>
  );
}

export default NavBar;
