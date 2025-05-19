import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchNewsById } from "./api";
import {Helmet} from "react-helmet";

import "./style.css";

import useGtag from "./useGtag";

function News({ onSearch }) {
  const { id } = useParams();
  const [news, setNews] = useState(null);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  useGtag();

  const [copied, setCopied] = useState(false);
  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };
  
  useEffect(() => {
    if (id && typeof id === "string") {
      fetchNewsById(id).then(data => {
        if (data) {
          setNews(data);
          setLoading(false); // 資料加載完畢後，設置 loading 為 false
        } else {
          navigate("/Notfound"); // 若找不到資料則跳轉
        }
      });
    } else {
      console.error("Invalid ID:", id);
    }
  }, [id]);
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
  };

  if (!news) return (<div className="loading-container">
    <img src="/tyre.svg" alt="Loading..." className='loading-spinner'/>
    <p>文章讀取中，請稍候...</p>
  </div>);

  const content = news.content_zh

  return (
    <>
    <Helmet>
      <title>{news.title_zh}</title>
      <meta property="og:title" content={news.title_zh} />
      <meta property="og:description" content={news.content_zh?.substring(0, 100) + "..."} />
      <meta property="og:type" content="article" />
      <meta property="og:url" content={window.location.to} />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={news.title_zh} />
      <meta name="twitter:description" content={news.content_zh?.substring(0, 100) + "..."} />
      
    </Helmet>
    <div className="main">
    {loading ? (
      <div className="loading-container">
        <img src="/tyre.svg" alt="Loading..." className='loading-spinner'/>
        <p>文章讀取中，請稍候...</p>
      </div>
    ) : news ? (  // 這裡使用 news 而不是 newsList
      <>
        <div className="news-container">
          <h1 className="news-title">{news.title_zh}</h1>
          <div className="news-meta">
            <span className="news-author">作者：{news.author}</span>
            <span className="news-date-separator"> | </span>
            <span className="news-date">日期：{formatDate(news.published_at)}</span>
          </div>
          <div className="news-share">
            <span>分享這篇文章：</span>
            <a
              href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.href)}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <i className="fa-brands fa-facebook"></i>
            </a>
            <a
              href={`https://twitter.com/intent/tweet?url=${encodeURIComponent(window.location.href)}&text=${encodeURIComponent(news.title_zh)}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <i className="fa-brands fa-twitter"></i>
            </a>
            <a
              href={`https://social-plugins.line.me/lineit/share?url=${encodeURIComponent(window.location.href)}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <i className="fa-brands fa-line"></i>
            </a>
            <button onClick={handleCopyLink}>
              {copied ? "已複製！" : "複製連結"}
            </button>
          </div>

          {news.link && (
            <div className="news-link">
              <a to={news.link} target="_blank" rel="noopener noreferrer">原文網站</a>
            </div>
          )}
          <div className="news-content" dangerouslySetInnerHTML={{ __html: content }} />
        </div>
      </>
    ) : (
      <p>目前查無資料</p>
    )}

    </div>
    
    </>
  );
}

export default News;
