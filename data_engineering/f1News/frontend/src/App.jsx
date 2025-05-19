import { useState, useEffect } from "react";
import NavBar from "./components/NavBar";
import Footer from "./components/Footer";
import { fetchNews } from "./api";
import { Link } from "react-router-dom";
import Masonry from 'react-masonry-css';
import useGtag from "./useGtag";
import "./style.css";

function App({ onSearch, searchResults }) {
  const [newsList, setNewsList] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const pageSize = 20;
  useGtag();
  useEffect(() => {
    setLoading(true); // 開始載入

    if (searchResults && searchResults.length > 0) {
      setNewsList(searchResults);
      setTotalPages(1);
      setLoading(false);
    } else {
      fetchNews(page, pageSize)
        .then(data => {
          setNewsList(data.news);
          setTotalPages(Math.ceil(data.total_count / pageSize));
          setLoading(false);
        })
        .catch(error => {
          console.error("載入資料發生錯誤:", error);
          setNewsList([]);
          setLoading(false);
        });
    }
  }, [page, searchResults]);

  const handleNextPage = () => {
    if (page < totalPages) setPage(prevPage => prevPage + 1);
  };

  const handlePreviousPage = () => {
    if (page > 1) setPage(prevPage => prevPage - 1);
  };

  function stripHtml(html) {
    const doc = new DOMParser().parseFromString(html, "text/html");
    return doc.body.textContent || "";
  }

  const breakpointColumnsObj = {
    default: 3,
    1024: 2,
    768: 1
  };

  return (
    <div className="main">
      <div className="container">
        <p className="main-introduction">
          新聞每天台灣時間8:00開始更新，會依照新聞的多寡而決定花費多少時間。
        </p>

        {loading ? (
          <div className="loading-container">
            <img src="/tyre.svg" alt="Loading..." className='loading-spinner'/>
            <p>文章讀取中，請稍候...</p>
          </div>
        ) : newsList.length > 0 ? (
          <>
            <div className="card-container">
              <Masonry
                breakpointCols={breakpointColumnsObj}
                className="masonry-grid"
                columnClassName="masonry-grid-column"
              >
                {newsList.map((news) => (
                  <Link to={`/news/${news.id}`} key={news.id} className="card-link">
                    <div className="card">
                      <h2 className="card-title">{news.title_zh}</h2>
                      {news.image_url && (
                        <img
                          src={news.image_url}
                          alt="news preview"
                          className="card-image"
                        />
                      )}
                      <div className="card-meta">
                        <p className="card-source">來源：{news.source || "未知"}</p>
                        <p className="card-author">作者：{news.author || "未知"}</p>
                        <p className="card-date">
                          日期：{new Date(news.published_at).toISOString().split("T")[0]}
                        </p>
                      </div>
                      <p className="card-content">
                        {news.content_zh
                          ? news.content_zh.replace(/<[^>]*>?/gm, '').substring(0, 100) + "..."
                          : "內容不可用"}
                      </p>
                    </div>
                  </Link>
                ))}
              </Masonry>
            </div>

            <div className="pagination">
              <button onClick={handlePreviousPage} disabled={page === 1 || isLoading}>
                上一頁
              </button>
              <span className="pagination-info">
                第 {page} 頁，共 {totalPages} 頁
              </span>
              <button onClick={handleNextPage} disabled={page === totalPages || isLoading}>
                下一頁
              </button>
            </div>
          </>
        ) : (
          <p>目前查無資料</p>
        )}
      </div>
    </div>
  );
}

export default App;
