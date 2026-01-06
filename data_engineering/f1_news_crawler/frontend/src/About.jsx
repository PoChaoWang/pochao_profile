import NavBar from "./components/NavBar";
import Footer from "./components/Footer";
function About({ onSearch }) {
    
  
    return (
      <>
        <div className="main">
          <div className="container">
          <div className="about-container">
              <h2>關於這個網站</h2>
              <p className="introduction">
              這些新聞內容主要透過 <strong>BBC</strong>、<strong>AutoSport</strong>、<strong>MotoSport</strong> 以及 <strong>RaceFans</strong> 的 RSS 來源獲取，並由 AI（gemini-2.0-flash）協助翻譯為繁體中文。雖然已盡可能設定使用繁體字，並保留英文人名的原文形式，但仍可能出現簡體中文或中文譯名的情況，若有錯誤，請以附上的原文連結為準。
              <br /><br />
              另外，由於爬取過程中有時會遇到一些未預期的狀況，可能導致部分資料清理不完全，因此在排版或格式上偶爾會出現不一致的情形，還請見諒。
              <br /><br />
              基於著作權考量，原始文章中若含有圖表或照片，我都不會擷取。相關系統目前仍在持續優化中，包含爬蟲流程與翻譯品質，感謝理解與包容。
              <br /><br />
              <br /><br />
              The news content is primarily sourced from the RSS feeds of BBC, AutoSport, MotoSport, and RaceFans, and translated into Traditional Chinese with the assistance of AI (gemini-2.0-flash). While efforts have been made to use Traditional Chinese characters and retain the original English names, occasional instances of Simplified Chinese or translated names may still appear. In case of any discrepancies, please refer to the attached original article links.
              <br /><br />
              Additionally, due to occasional unexpected issues during the scraping process, some data may not be fully cleaned, which can result in occasional inconsistencies in formatting or layout. We apologize for any inconvenience.
              <br /><br />
              For copyright reasons, images or charts included in the original articles are not extracted. The system is still being actively improved, including the scraping process and translation quality. Thank you for your understanding and support.
              </p>
              
              
          </div>
          </div>
          
        </div>
      </>
    );
  }
  
  export default About;
  