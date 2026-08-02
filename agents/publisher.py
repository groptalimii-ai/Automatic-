"""
🚀 Publisher Agent
===================
وكيل النشر - يرفع المنتجات على Gumroad ويدير المتجر
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

import yaml
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

console = Console()


@dataclass
class PublishedProduct:
    """منتج منشور"""
    gumroad_id: str
    name: str
    url: str
    price: float
    status: str
    published_at: str


class PublisherAgent:
    """
    🚀 وكيل النشر

    يقوم بـ:
    - إنشاء منتجات على Gumroad
    - رفع الملفات
    - كتابة الوصف التسويقي
    - ضبط الأسعار والعروض
    - إدارة الحزم (Bundles)
    """

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)
        self.client = OpenAI(api_key=self.config["api_keys"]["openai"])
        self.gumroad_token = self.config["api_keys"].get("gumroad", "")
        self.base_url = "https://api.gumroad.com/v2"
        console.print(Panel(
            "[bold green]🚀 Publisher Agent Initialized[/bold green]",
            border_style="green"
        ))

    def generate_sales_copy(
        self,
        product_name: str,
        product_type: str,
        target_audience: str,
        key_benefits: List[str],
        price: float
    ) -> Dict[str, str]:
        """توليد نسخة مبيعات احترافية"""
        console.print(f"
[bold yellow]📝 Generating Sales Copy for: {product_name}...[/bold yellow]")

        prompt = f"""
        Create compelling sales copy for a digital product.

        Product: {product_name}
        Type: {product_type}
        Audience: {target_audience}
        Price: ${price}
        Key Benefits: {key_benefits}

        Generate:
        1. Headline (attention-grabbing, under 15 words)
        2. Subheadline (expands on the promise)
        3. Product Description (3-4 paragraphs, benefits-focused)
        4. Bullet Points (5-7 key benefits)
        5. Call to Action (urgent, clear)
        6. FAQ (3-5 common questions with answers)
        7. SEO Title (60 chars max)
        8. SEO Description (160 chars max)
        9. Tags (10 relevant keywords)

        Return as JSON:
        {{
            "headline": "...",
            "subheadline": "...",
            "description": "...",
            "bullets": ["..."],
            "cta": "...",
            "faq": [{{"q": "...", "a": "..."}}],
            "seo_title": "...",
            "seo_description": "...",
            "tags": ["..."]
        }}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=2500
        )

        try:
            content_text = response.choices[0].message.content
            json_start = content_text.find("{")
            json_end = content_text.rfind("}") + 1
            sales_copy = json.loads(content_text[json_start:json_end])
        except:
            sales_copy = {
                "headline": product_name,
                "description": f"Get {product_name} today!",
                "bullets": key_benefits,
                "tags": [product_type, "digital", "download"]
            }

        console.print(f"   ✅ Sales copy generated: {len(sales_copy.get('bullets', []))} bullets")
        return sales_copy

    def create_gumroad_product(
        self,
        name: str,
        description: str,
        price: float,
        file_path: str,
        cover_image: Optional[str] = None,
        tags: List[str] = None,
        custom_permalink: Optional[str] = None
    ) -> PublishedProduct:
        """إنشاء منتج على Gumroad"""
        console.print(f"
[bold yellow]🚀 Publishing to Gumroad: {name}...[/bold yellow]")

        if not self.gumroad_token:
            console.print("   ⚠️  Gumroad token not configured. Simulating publish...")
            return PublishedProduct(
                gumroad_id="simulated_" + datetime.now().strftime("%Y%m%d%H%M%S"),
                name=name,
                url=f"https://gumroad.com/l/{custom_permalink or name.lower().replace(' ', '-')}",
                price=price,
                status="simulated",
                published_at=datetime.now().isoformat()
            )

        try:
            # Create product
            url = f"{self.base_url}/products"
            data = {
                "name": name,
                "description": description,
                "price": int(price * 100),  # Convert to cents
                "currency": "usd",
                "custom_permalink": custom_permalink or name.lower().replace(" ", "-"),
                "custom_receipt": f"Thank you for purchasing {name}!",
                "is_physical": False,
                "shown_on_profile": True,
                "require_shipping": False
            }

            headers = {"Authorization": f"Bearer {self.gumroad_token}"}
            response = requests.post(url, headers=headers, data=data)
            response_data = response.json()

            if "product" in response_data:
                product_id = response_data["product"]["id"]
                short_url = response_data["product"].get("short_url", "")

                # Upload file
                if os.path.exists(file_path):
                    self._upload_file(product_id, file_path)

                # Upload cover
                if cover_image and os.path.exists(cover_image):
                    self._upload_cover(product_id, cover_image)

                console.print(f"   ✅ Published! URL: {short_url}")

                return PublishedProduct(
                    gumroad_id=product_id,
                    name=name,
                    url=short_url,
                    price=price,
                    status="published",
                    published_at=datetime.now().isoformat()
                )
            else:
                console.print(f"   ❌ Error: {response_data.get('message', 'Unknown error')}")
                return PublishedProduct(
                    gumroad_id="error",
                    name=name,
                    url="",
                    price=price,
                    status="failed",
                    published_at=datetime.now().isoformat()
                )

        except Exception as e:
            console.print(f"   ❌ Error publishing: {str(e)}")
            return PublishedProduct(
                gumroad_id="error",
                name=name,
                url="",
                price=price,
                status="failed",
                published_at=datetime.now().isoformat()
            )

    def _upload_file(self, product_id: str, file_path: str):
        """رفع ملف على Gumroad"""
        url = f"{self.base_url}/products/{product_id}/resource_subscriptions"
        headers = {"Authorization": f"Bearer {self.gumroad_token}"}

        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.put(url, headers=headers, files=files)

        if response.status_code == 200:
            console.print("   ✅ File uploaded successfully")
        else:
            console.print(f"   ⚠️  File upload status: {response.status_code}")

    def _upload_cover(self, product_id: str, cover_path: str):
        """رفع صورة غلاف"""
        url = f"{self.base_url}/products/{product_id}"
        headers = {"Authorization": f"Bearer {self.gumroad_token}"}

        with open(cover_path, "rb") as f:
            files = {"thumbnail": f}
            response = requests.put(url, headers=headers, files=files)

        if response.status_code == 200:
            console.print("   ✅ Cover image uploaded")

    def create_bundle(
        self,
        bundle_name: str,
        products: List[PublishedProduct],
        bundle_price: float,
        description: str = ""
    ) -> PublishedProduct:
        """إنشاء حزمة منتجات"""
        console.print(f"
[bold yellow]🎁 Creating Bundle: {bundle_name}...[/bold yellow]")

        # Note: Gumroad doesn't have a native bundle API, so we create a product
        # that references other products or includes all files

        bundle_description = description or f"Get {len(products)} premium products at a special price!

Includes:
"
        for p in products:
            bundle_description += f"- {p.name}
"

        return self.create_gumroad_product(
            name=bundle_name,
            description=bundle_description,
            price=bundle_price,
            file_path="products/bundle_info.txt",  # Placeholder
            custom_permalink=bundle_name.lower().replace(" ", "-")
        )

    def generate_pricing_strategy(
        self,
        product_type: str,
        market_data: Dict,
        production_cost: float = 0
    ) -> Dict:
        """توليد استراتيجية تسعير"""
        console.print(f"
[bold yellow]💰 Generating Pricing Strategy...[/bold yellow]")

        prompt = f"""
        Analyze and recommend optimal pricing for a digital product.

        Product Type: {product_type}
        Market Average: ${market_data.get('average_price', 20)}
        Competition Level: {market_data.get('competition_level', 'medium')}
        Production Cost: ${production_cost}

        Recommend:
        1. Optimal launch price
        2. Premium price (with extra value)
        3. Discount strategy
        4. Bundle pricing
        5. Subscription option (if applicable)

        Return as JSON with reasoning.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=1000
        )

        try:
            content_text = response.choices[0].message.content
            json_start = content_text.find("{")
            json_end = content_text.rfind("}") + 1
            pricing = json.loads(content_text[json_start:json_end])
        except:
            pricing = {
                "launch_price": 19,
                "premium_price": 47,
                "strategy": "Start low, increase with social proof"
            }

        console.print(f"   ✅ Pricing: Launch ${pricing.get('launch_price', 19)} | Premium ${pricing.get('premium_price', 47)}")
        return pricing


if __name__ == "__main__":
    agent = PublisherAgent()
    copy = agent.generate_sales_copy(
        "Productivity Toolkit",
        "template",
        "remote workers",
        ["Save 5 hours/week", "Better focus", "Less stress"],
        27
    )
    print(copy["headline"])
