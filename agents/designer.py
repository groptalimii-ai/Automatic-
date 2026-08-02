"""
🎨 Designer Agent
==================
وكيل التصميم - ينتج الصور والأغلفة والرسومات
"""

import os
import base64
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
class DesignAsset:
    """أصل تصميمي"""
    asset_type: str
    prompt: str
    file_path: Optional[str] = None
    url: Optional[str] = None
    dimensions: str = "1024x1024"


class DesignerAgent:
    """
    🎨 وكيل التصميم
    
    ينتج:
    - أغلفة كتب إلكترونية
    - صور تسويقية
    - رسومات توضيحية
    - أيقونات وعناصر بصرية
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)
        self.client = OpenAI(api_key=self.config["api_keys"]["openai"])
        console.print(Panel(
            "[bold magenta]🎨 Designer Agent Initialized[/bold magenta]",
            border_style="magenta"
        ))
    
    def generate_cover(
        self,
        title: str,
        subtitle: str = "",
        style: str = "modern minimalist",
        size: str = "1024x1024"
    ) -> DesignAsset:
        """توليد غلاف كتاب إلكتروني باستخدام DALL-E 3"""
        console.print(f"\n[bold yellow]🎨 Generating Book Cover: {title}...[/bold yellow]")
        
        prompt = f"""
        Professional book cover design for: "{title}"
        {f"Subtitle: {subtitle}" if subtitle else ""}
        Style: {style}
        Requirements:
        - Clean, professional, eye-catching
        - Suitable for digital product marketplace
        - No text on the image (just visual design)
        - High quality, detailed
        """
        
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            # تحميل الصورة
            os.makedirs("products/images", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"products/images/cover_{timestamp}.png"
            
            img_data = requests.get(image_url).content
            with open(filename, "wb") as img_file:
                img_file.write(img_data)
            
            console.print(f"   ✅ Cover saved: {filename}")
            
            return DesignAsset(
                asset_type="book_cover",
                prompt=prompt,
                file_path=filename,
                url=image_url,
                dimensions=size
            )
            
        except Exception as e:
            console.print(f"   ❌ Error generating cover: {str(e)}")
            return DesignAsset(asset_type="book_cover", prompt=prompt, dimensions=size)
    
    def generate_marketing_images(
        self,
        product_name: str,
        count: int = 3,
        style: str = "modern digital art"
    ) -> List[DesignAsset]:
        """توليد صور تسويقية متعددة"""
        console.print(f"\n[bold yellow]🎨 Generating {count} Marketing Images...[/bold yellow]")
        
        assets = []
        
        for i in range(count):
            prompt = f"""
            Marketing image for digital product: "{product_name}"
            Style: {style}
            Purpose: Social media promotion, Gumroad listing
            - Clean background
            - Professional look
            - No text, just visual elements
            - Variation {i+1} of {count}
            """
            
            try:
                response = self.client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1
                )
                
                image_url = response.data[0].url
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"products/images/marketing_{timestamp}_{i+1}.png"
                
                img_data = requests.get(image_url).content
                with open(filename, "wb") as img_file:
                    img_file.write(img_data)
                
                assets.append(DesignAsset(
                    asset_type="marketing",
                    prompt=prompt,
                    file_path=filename,
                    url=image_url
                ))
                console.print(f"   ✅ Image {i+1} saved")
                
            except Exception as e:
                console.print(f"   ⚠️  Image {i+1} failed: {str(e)}")
        
        return assets
    
    def generate_thumbnail(
        self,
        title: str,
        description: str = ""
    ) -> DesignAsset:
        """توليد صورة مصغرة للمنتج"""
        return self.generate_cover(title, description, style="bold thumbnail", size="1024x1024")


if __name__ == "__main__":
    agent = DesignerAgent()
    cover = agent.generate_cover("The Productivity Blueprint")
    print(f"Cover: {cover.file_path}")
