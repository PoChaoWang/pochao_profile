import React, { useState } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import News from "./News";
import Search from "./Search";
import NotFound from "./NotFound";
import About from "./About";
import { searchNews } from "./api";
import NavBar from "./components/NavBar";
import Footer from "./components/Footer";

function Main() {
  const [searchResults, setSearchResults] = useState([]);

  const handleSearch = async (query) => {
    const results = await searchNews(query);
    setSearchResults(results);
  };

  return (
    <BrowserRouter>
      <NavBar onSearch={handleSearch} />
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/about" element={<About />} />
          <Route path="/news/:id" element={<News />} />
          <Route path="/search" element={<Search onSearch={handleSearch} />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      <Footer />
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<Main />);