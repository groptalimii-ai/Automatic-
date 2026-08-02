"""
🎯 Market Research Agent
=========================
وكيل أبحاث السوق - يحلل اتجاهات السوق ويحدد أفضل المنتجات الرقمية المربحة
"""

import json
import time
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

import yaml
from openai import OpenAI
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@dataclass
class ProductIdea:
    """فكرة منتج رقمي مولدة من التحليل"""
    title: str
    description: str
    product_type: str
    target_audience: str
    estimated_price: float
    demand_score: float
    competition_score: float
    profit_potential: float
    ease_of_creation: float
    overall_score: float
    keywords: List[str]
    content_outline: List[str]
    estimated_time_hours: float
    data_sources: List[str]


@dataclass
class MarketAnalysis:
    """نتائج تحليل السوق الكامل"""
    niche: str
    trend_score: float
    search_volume: str
    top_keywords: List[str]
    competitor_analysis: str
    audience_pain_points: List[str]
    recommended_products: List[ProductIdea]
    timestamp: str


class MarketResearchAgent:
    """
    🤖 وكيل أبحاث السوق
    
    يقوم بـ:
    - تحليل اتجاهات Google Trends
    - تحليل Reddit لمعرفة مشاكل الجمهور
    - تحليل منتجات Gumroad الشائعة
    - توليد أفكار منتجات مربحة باستخدام GPT-4
    - تقييم الأفكار وترتيبها حسب الربحية
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """تهيئة الوكيل بالإعدادات"""
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)
        
        self.openai_client = OpenAI(api_key=self.config["api_keys"]["openai"])
        self.model = self.config["agents"]["market_research"]["model"]
        self.temperature = self.config["agents"]["market_research"]["temperature"]
        
        console.print(Panel(
            "[bold cyan]🎯 Market Research Agent Initialized[/bold cyan]\n"
            f"Model: {self.model} | Temperature: {self.temperature}",
            border_style="cyan"
        ))
    
    # ═══════════════════════════════════════════════════════
    # 1. تحليل Google Trends
    # ═══════════════════════════════════════════════════════
    
    def analyze_google_trends(self, keywords: List[str]) -> Dict:
        """تحليل اتجاهات البحث في Google Trends"""
        console.print("\n[bold yellow]🔍 Step 1: Analyzing Google Trends...[/bold yellow]")
        
        try:
            from pytrends.request import TrendReq
            
            pytrends = TrendReq(
                hl=self.config["market_research"]["google_trends"]["hl"],
                tz=self.config["market_research"]["google_trends"]["tz"]
            )
            
            results = {}
            for keyword in keywords:
                try:
                    pytrends.build_payload(
                        [keyword],
                        cat=0,
                        timeframe=self.config["market_research"]["google_trends"]["timeframe"],
                        geo=self.config["market_research"]["google_trends"]["geo"]
                    )
                    
                    interest_over_time = pytrends.interest_over_time()
                    
                    if not interest_over_time.empty:
                        avg_interest = interest_over_time[keyword].mean()
                        last_val = interest_over_time[keyword].iloc[-1]
                        first_val = interest_over_time[keyword].iloc[0]
                        trend_dir = "📈 صاعد" if last_val > first_val else "📉 هابط"
                        
                        results[keyword] = {
                            "average_interest": round(avg_interest, 2),
                            "trend_direction": trend_dir,
                            "peak_month": interest_over_time[keyword].idxmax().strftime("%Y-%m")
                        }
                        
                        console.print(f"   ✅ {keyword}: متوسط الاهتمام {avg_interest:.1f}/100 | {trend_dir}")
                    
                    time.sleep(1)
                    
                except Exception as e:
                    console.print(f"   ⚠️  خطأ في تحليل '{keyword}': {str(e)}")
                    results[keyword] = {"error": str(e)}
            
            return results
            
        except ImportError:
            console.print("   ⚠️  pytrends غير مثبت، سيتم استخدام التحليل الذكي فقط")
            return {}
    
    # ═══════════════════════════════════════════════════════
    # 2. تحليل Reddit
    # ═══════════════════════════════════════════════════════
    
    def analyze_reddit(self, niche: str, limit: int = 50) -> Dict:
        """تحليل منشورات Reddit لفهم مشاكل الجمهور"""
        console.print("\n[bold yellow]🔍 Step 2: Analyzing Reddit Discussions...[/bold yellow]")
        
        try:
            import praw
            
            reddit_config = self.config["market_research"]["reddit"]
            reddit = praw.Reddit(
                client_id=reddit_config["client_id"],
                client_secret=reddit_config["client_secret"],
                user_agent=reddit_config["user_agent"]
            )
            
            pain_points = []
            popular_topics = []
            
            for subreddit_name in reddit_config["subreddits"]:
                try:
                    subreddit = reddit.subreddit(subreddit_name)
                    per_sub = limit // len(reddit_config["subreddits"])
                    
                    for post in subreddit.search(niche, limit=per_sub):
                        if post.score > 5:
                            popular_topics.append({
                                "title": post.title,
                                "score": post.score,
                                "comments": post.num_comments,
                                "subreddit": subreddit_name
                            })
                            
                            pain_words = ["struggle", "problem", "issue", "help", "need", "how to",
                                          "difficult", "hard", "can not", "will not", "frustrated",
                                          "stress", "overwhelmed", "stuck", "confused"]
                            if any(w in post.title.lower() for w in pain_words):
                                pain_points.append(post.title)
                
                except Exception as e:
                    console.print(f"   ⚠️  خطأ في r/{subreddit_name}: {str(e)}")
            
            popular_topics.sort(key=lambda x: x["score"], reverse=True)
            
            console.print(f"   ✅ تم جمع {len(pain_points)} نقطة ألم و {len(popular_topics)} موضوع شائع")
            
            return {
                "pain_points": list(set(pain_points))[:20],
                "popular_topics": popular_topics[:15],
                "total_posts_analyzed": len(popular_topics)
            }
            
        except ImportError:
            console.print("   ⚠️  praw غير مثبت، سيتم تخطي تحليل Reddit")
            return {"pain_points": [], "popular_topics": [], "total_posts_analyzed": 0}
    
    # ═══════════════════════════════════════════════════════
    # 3. تحليل Gumroad بالذكاء الاصطناعي
    # ═══════════════════════════════════════════════════════
    
    def analyze_gumroad_market(self, niche: str) -> Dict:
        """تحليل سوق Gumroad باستخدام الذكاء الاصطناعي"""
        console.print("\n[bold yellow]🔍 Step 3: Analyzing Gumroad Marketplace...[/bold yellow]")
        
        prompt = f"""
        أنت خبير في تحليل سوق المنتجات الرقمية على Gumroad.
        حلل المنافسة في مجال: "{niche}"
        
        قدم تحليلاً واقعياً يشمل:
        1. عدد المنتجات المتاحة تقريباً
        2. متوسط الأسعار
        3. أفضل البائعين (أنواعهم)
        4. نقاط الضعف في المنتجات الحالية
        5. الفرص المتاحة للمنتجات الجديدة
        
        قدم الإجابة بتنسيق JSON فقط:
        {{
            "estimated_competitors": عدد صحيح,
            "average_price": رقم عشري,
            "price_range": {{"min": رقم, "max": رقم}},
            "top_seller_types": ["نوع1", "نوع2"],
            "market_gaps": ["فجوة1", "فجوة2"],
            "weaknesses_in_current_products": ["نقطة ضعف1", "نقطة ضعف2"],
            "opportunities": ["فرصة1", "فرصة2"],
            "competition_level": "منخفض|متوسط|عالي",
            "market_maturity": "ناشئ|متوسط|ناضج"
        }}
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=1500
        )
        
        try:
            content = response.choices[0].message.content
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                result = json.loads(content[json_start:json_end])
            else:
                result = json.loads(content)
            
            comp = result.get("competition_level", "N/A")
            mat = result.get("market_maturity", "N/A")
            console.print(f"   ✅ تم تحليل السوق: {comp} تنافس | {mat} نضج")
            return result
            
        except Exception as e:
            console.print(f"   ⚠️  خطأ في تحليل Gumroad: {str(e)}")
            return {}
