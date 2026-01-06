import axios from "axios";

const API_URL = "https://f1news-scraper.onrender.com";

export const fetchNews = async (page = 1, pageSize = 20) => {
  try {
    const response = await axios.get(`${API_URL}/index`, {  // 改回 /
      params: { page, page_size: pageSize },
    });
    console.log(response.data);
    return response.data;
  } catch (error) {
    console.error("Error fetching news:", error);
    if (error.response && error.response.status === 404) {
      window.location.href = "/NotFound";
    }
    return { news: [], total_count: 0 };
  }
};

export const fetchNewsById = async (id) => {
  try {
    console.log("Fetching news by ID:", `${API_URL}/news/${id}`); // 更新路徑
    const response = await axios.get(`${API_URL}/news/${id}`); // 使用新的路徑
    return response.data.news;
  } catch (error) {
    console.error("Error fetching news by ID:", error);
    if (error.response && error.response.status === 404) {
      window.location.href = "/NotFound";
      console.error("404 Not Found: ", error);
    }
    return null;
  }
};

export async function searchNews(query) {
  try {
    const response = await fetch(`${API_URL}/search?q=${query}`);
    if (!response.ok) {
      throw new Error("Failed to fetch search results");
    }
    return await response.json(); // 確保返回 JSON 格式的結果
  } catch (error) {
    console.error("Error searching news:", error);
    if (error.response && error.response.status === 404) {
      window.location.href = "/NotFound";
    }
    return [];
  }
}
