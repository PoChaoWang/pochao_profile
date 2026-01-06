import { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import NavBar from "./components/NavBar";
import Footer from "./components/Footer";
import { searchNews } from "./api";
import Masonry from 'react-masonry-css';
import "./style.css";
import useGtag from "./useGtag";

function Search({ onSearch }) {
  const [searchResults, setSearchResults] = useState([]);
  const [query] = useSearchParams(); // 獲取 URL 中的搜尋參數
  const searchQuery = query.get("q"); // 取得搜尋關鍵字
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true); // 添加載入狀態

  useGtag(); 
  useEffect(() => {
    if (searchQuery) {
      setLoading(true); // 開始載入
      searchNews(searchQuery).then((results) => {
        setSearchResults(results);
        setTotalPages(Math.ceil(results.length / 20)); // 假設每頁顯示 20 筆資料
        setLoading(false); // 載入完成
      }).catch(error => {
        console.error("搜尋出錯:", error);
        setLoading(false); // 出錯時也需要結束載入狀態
      });
    } else {
      setLoading(false); // 如果沒有搜尋關鍵字，也結束載入狀態
    }
  }, [searchQuery]);

  function stripHtml(html) {
    const doc = new DOMParser().parseFromString(html, "text/html");
    return doc.body.textContent || "";
  }

  const breakpointColumnsObj = {
    default: 3,
    1024: 2,
    768: 1
  };

  const handleNextPage = () => {
    setPage(prevPage => prevPage + 1);
  };

  const handlePreviousPage = () => {
    if (page > 1) {
      setPage(prevPage => prevPage - 1);
    }
  };

  return (
    <div className="main">
      <div className="container">
        <h1>搜尋結果：{searchQuery}</h1>
        {loading ? (
          <div className="loading-container">
            <img src="/tyre.svg" alt="Loading..." className='loading-spinner'/>
            <p>搜尋中，請稍候...</p>
            <div className="loading-spinner"></div>
          </div>
        ) : searchResults.length > 0 ? (
          <>
            <div className="card-container">
              <Masonry
                breakpointCols={breakpointColumnsObj}
                className="masonry-grid"
                columnClassName="masonry-grid-column">
                {searchResults.map(news => (
                  <Link to={`/news/${news.id}`} className="card-link" key={news.id}>
                    <div className="card">
                      <h2 className="card-title">{news.title_zh}</h2>
                      {news.image_url && news.image_url !== null && (
                        <img
                          src={news.image_url}
                          alt="news preview"
                          className="card-image"
                          style={{ width: "100%", maxHeight: "200px", objectFit: "cover", marginTop: "8px" }}
                        />
                      )}
                      <div className="card-meta">
                        <p className="card-source">作者：{news.source || "未知"}</p>
                        <p className="card-author">作者：{news.author || "未知"}</p>
                        <p className="card-date">日期：{new Date(news.published_at).toISOString().split("T")[0]}</p>
                      </div>
                      <p className="card-content">
                        {news.content_zh ? stripHtml(news.content_zh).substring(0, 100) + "..." : "內容不可用"}
                      </p>
                    </div>
                  </Link>
                ))}
              </Masonry>
            </div>
            <div className="pagination">
              <button onClick={handlePreviousPage} disabled={page === 1}>
                上一頁
              </button>
              <span className="pagination-info">
                第 {page} 頁，共 {totalPages} 頁
              </span>
              <button onClick={handleNextPage} disabled={page === totalPages}>
                下一頁
              </button>
            </div>
          </>
        ) : (
          <p>沒有找到相關結果。</p>
        )}
      </div>
    </div>
  );
}

export default Search;