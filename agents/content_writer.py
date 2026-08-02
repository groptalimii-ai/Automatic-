"""
✍️ Content Writer Agent
========================
وكيل الكتابة - ينتج المحتوى النصي للكتب والقوالب والدورات
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

import yaml
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

console = Console()


@dataclass
class WrittenContent:
    """محتوى مكتوب جاهز للنشر"""
    title: str
    content_type: str
    full_text: str
    chapters: List[Dict]
    word_count: int
    seo_description: str
    marketing_copy: str
    tags: List[str]
    file_path: Optional[str] = None


class ContentWriterAgent:
    """
    ✍️ وكيل الكتابة
    
    ينتج:
    - كتب إلكترونية (ebooks)
    - كتب مصورة (comics/storyboards)
    - قوالب نصية
    - محتوى تسويقي
    - دورات تدريبية (scripts)
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)
        self.client = OpenAI(api_key=self.config["api_keys"]["openai"])
        self.model = self.config["agents"]["content_writer"]["model"]
        console.print(Panel(
            "[bold green]✍️ Content Writer Agent Initialized[/bold green]",
            border_style="green"
        ))
    
    def _generate_with_ai(self, prompt: str, max_tokens: int = 4000, temp: float = None) -> str:
        """توليد نص باستخدام GPT-4"""
        if temp is None:
            temp = self.config["agents"]["content_writer"]["temperature"]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temp,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def write_ebook(
        self,
        title: str,
        outline: List[str],
        target_pages: int = 50,
        tone: str = "professional",
        language: str = "en"
    ) -> WrittenContent:
        """
        كتابة كتاب إلكتروني كامل
        
        Args:
            title: عنوان الكتاب
            outline: قائمة بالفصول
            target_pages: عدد الصفحات المستهدف
            tone: نمط الكتابة (professional, casual, inspirational...)
            language: اللغة (en, ar)
        """
        console.print(f"\n[bold yellow]📚 Writing Ebook: {title}...[/bold yellow]")
        
        chapters = []
        full_text = f"# {title}\n\n"
        
        for i, chapter_title in enumerate(outline, 1):
            console.print(f"   📝 Writing Chapter {i}/{len(outline)}: {chapter_title}")
            
            prompt = f"""
            اكتب فصلاً كاملاً لكتاب إلكتروني.
            
            عنوان الكتاب: {title}
            عنوان الفصل {i}: {chapter_title}
            نمط الكتابة: {tone}
            اللغة: {language}
            الطول المستهدف: حوالي {target_pages * 300 // len(outline)} كلمة
            
            المتطلبات:
            - محتوى عميق وقيم
            - أمثلة عملية
            - خطوات قابلة للتنفيذ
            - بدون مقدمة أو خاتمة للفصل (فقط المحتوى)
            
            اكتب الفصل الآن:
            """
            
            chapter_text = self._generate_with_ai(prompt, max_tokens=3500, temp=0.7)
            
            chapters.append({
                "number": i,
                "title": chapter_title,
                "content": chapter_text,
                "word_count": len(chapter_text.split())
            })
            
            full_text += f"## الفصل {i}: {chapter_title}\n\n{chapter_text}\n\n---\n\n"
        
        # توليد الوصف التسويقي
        marketing_prompt = f"""
        اكتب وصفاً تسويقياً جذاباً (3-4 جمل) لكتاب إلكتروني بعنوان: "{title}"
        الوصف يجب أن ي:
        - يجذب الانتباه فوراً
        - يوضح الفائدة الرئيسية
        - يحتوي على دعوة للعمل
        """
        marketing_copy = self._generate_with_ai(marketing_prompt, max_tokens=500, temp=0.8)
        
        # توليد SEO description
        seo_prompt = f"""اكتب وصف SEO (150-160 حرف) لكتاب: {title}"""
        seo_desc = self._generate_with_ai(seo_prompt, max_tokens=200, temp=0.3)
        
        word_count = len(full_text.split())
        
        console.print(f"   ✅ Ebook Complete: {word_count} words | {len(chapters)} chapters")
        
        return WrittenContent(
            title=title,
            content_type="ebook",
            full_text=full_text,
            chapters=chapters,
            word_count=word_count,
            seo_description=seo_desc,
            marketing_copy=marketing_copy,
            tags=[]
        )
    
    def write_template_guide(
        self,
        template_name: str,
        template_type: str,
        sections: List[str]
    ) -> WrittenContent:
        """كتابة دليل لقالب (Notion, Excel, CRM...)"""
        console.print(f"\n[bold yellow]📋 Writing Template Guide: {template_name}...[/bold yellow]")
        
        prompt = f"""
        اكتب دليلاً شاملاً لقالب: {template_name}
        نوع القالب: {template_type}
        الأقسام المطلوبة: {sections}
        
        الدليل يجب أن يشمل:
        1. مقدمة عن القالب واستخداماته
        2. شرح كل قسم بالتفصيل
        3. أمثلة على كيفية الاستخدام
        4. نصائح للحصول على أقصى استفادة
        5. الأسئلة الشائعة
        
        اكتب الدليل الآن:
        """
        
        content = self._generate_with_ai(prompt, max_tokens=4000)
        
        return WrittenContent(
            title=template_name,
            content_type="template_guide",
            full_text=content,
            chapters=[{"title": s, "content": ""} for s in sections],
            word_count=len(content.split()),
            seo_description=f"Complete guide for {template_name}",
            marketing_copy=f"Master {template_name} with this comprehensive guide.",
            tags=[template_type, "template", "guide"]
        )
    
    def write_course_script(
        self,
        course_title: str,
        lessons: List[str],
        duration_per_lesson: int = 10
    ) -> WrittenContent:
        """كتابة سكريبت لدورة فيديو"""
        console.print(f"\n[bold yellow]🎓 Writing Course Script: {course_title}...[/bold yellow]")
        
        scripts = []
        full_text = f"# {course_title} - Course Script\n\n"
        
        for i, lesson in enumerate(lessons, 1):
            prompt = f"""
            اكتب سكريبت درس فيديو.
            عنوان الدورة: {course_title}
            الدرس {i}: {lesson}
            المدة المستهدفة: {duration_per_lesson} دقائق
            
            السكريبت يجب أن يشمل:
            - مقدمة جذابة
            - المحتوى الرئيسي (نقاط رئيسية)
            - أمثلة عملية
            - ملخص ودعوة للعمل
            - ملاحظات للمقدم (ما يظهر على الشاشة)
            
            اكتب السكريبت الآن:
            """
            
            script = self._generate_with_ai(prompt, max_tokens=3000)
            scripts.append({"lesson": i, "title": lesson, "script": script})
            full_text += f"## الدرس {i}: {lesson}\n\n{script}\n\n---\n\n"
            console.print(f"   ✅ Lesson {i} script written")
        
        return WrittenContent(
            title=course_title,
            content_type="course_script",
            full_text=full_text,
            chapters=scripts,
            word_count=len(full_text.split()),
            seo_description=f"{course_title} - Complete video course script",
            marketing_copy=f"Learn {course_title} with expert-led video lessons.",
            tags=["course", "video", "education"]
        )
    
    def save_content(self, content: WrittenContent, output_dir: str = "products") -> str:
        """حفظ المحتوى كملف Markdown"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/{content.content_type}_{timestamp}.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {content.title}\n\n")
            f.write(f"**Type:** {content.content_type}\n")
            f.write(f"**Words:** {content.word_count}\n")
            f.write(f"**SEO:** {content.seo_description}\n\n")
            f.write(f"**Marketing Copy:**\n{content.marketing_copy}\n\n---\n\n")
            f.write(content.full_text)
        
        content.file_path = filename
        console.print(f"[bold blue]💾 Saved to: {filename}[/bold blue]")
        return filename


if __name__ == "__main__":
    agent = ContentWriterAgent()
    ebook = agent.write_ebook(
        title="The Ultimate Productivity Guide",
        outline=[
            "Understanding Your Energy",
            "The Morning Routine Blueprint",
            "Deep Work Mastery",
            "Digital Minimalism",
            "Weekly Review System"
        ],
        target_pages=40
    )
    agent.save_content(ebook)
