"""
⚙️ Orchestrator v2.0
=====================
المنسق الرئيسي - يربط جميع الوكلاء ويدير سير العمل
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@dataclass
class ProductionJob:
    """مهمة إنتاج"""
    job_id: str
    niche: str
    product_type: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    product_data: Optional[Dict] = None
    gumroad_url: Optional[str] = None
    error: Optional[str] = None


class DigitalFactoryOrchestrator:
    """
    ⚙️ المنسق الرئيسي v2.0

    يدير سير العمل الكامل:
    1. أبحاث السوق → 2. إنتاج المحتوى → 3. التصميم → 4. النشر → 5. التسويق
    """

    def __init__(self, config_path: str = "config.yaml"):
        console.print(Panel(
            "[bold magenta]🏭 DIGITAL FACTORY ORCHESTRATOR v2.0[/bold magenta]\n"
            "AI-Powered Digital Product Factory with Web, Mobile, Email & Payments",
            border_style="magenta"
        ))

        self.config_path = config_path
        self.jobs: List[ProductionJob] = []
        self._load_agents()

    def _load_agents(self):
        """تحميل جميع الوكلاء (13 وكيل)"""
        console.print("\n[bold cyan]🤖 Loading AI Agents...[/bold cyan]")

        agents_to_load = [
            ("agents.market_research", "MarketResearchAgent", "market_agent"),
            ("agents.content_writer", "ContentWriterAgent", "writer_agent"),
            ("agents.designer", "DesignerAgent", "designer_agent"),
            ("agents.audio_agent", "AudioAgent", "audio_agent"),
            ("agents.video_agent", "VideoAgent", "video_agent"),
            ("agents.code_agent", "CodeAgent", "code_agent"),
            ("agents.business_agent", "BusinessAgent", "business_agent"),
            ("agents.health_agent", "HealthAgent", "health_agent"),
            ("agents.publisher", "PublisherAgent", "publisher_agent"),
            ("agents.email_agent", "EmailAgent", "email_agent"),
            ("agents.payment_agent", "PaymentAgent", "payment_agent"),
            ("agents.analytics_agent", "AnalyticsAgent", "analytics_agent"),
            ("agents.social_media_agent", "SocialMediaAgent", "social_agent"),
        ]

        for module_path, class_name, attr_name in agents_to_load:
            try:
                module = __import__(module_path, fromlist=[class_name])
                agent_class = getattr(module, class_name)
                setattr(self, attr_name, agent_class(self.config_path))
            except Exception as e:
                console.print(f"   ⚠️  {class_name}: {str(e)[:50]}")
                setattr(self, attr_name, None)

        console.print("   ✅ All agents loaded\n")

    # ═══════════════════════════════════════════════════════
    # سير العمل الرئيسي - إنتاج كتاب إلكتروني متكامل
    # ═══════════════════════════════════════════════════════

    def produce_ebook(
        self,
        niche: str,
        keywords: List[str],
        target_pages: int = 40,
        price: Optional[float] = None
    ) -> ProductionJob:
        """إنتاج كتاب إلكتروني كامل مع تسويق"""
        job_id = f"ebook_{datetime.now().strftime('%Y%m%d_%H%M%S')}""
        job = ProductionJob(
            job_id=job_id,
            niche=niche,
            product_type="ebook",
            status="researching",
            created_at=datetime.now().isoformat()
        )
        self.jobs.append(job)

        console.print(Panel(
            f"[bold green]🚀 Starting Full Production Pipeline: {niche}[/bold green]",
            border_style="green"
        ))

        try:
            # Phase 1: Market Research
            console.print("\n[bold cyan]📊 PHASE 1: Market Research[/bold cyan]")
            if self.market_agent:
                analysis = self.market_agent.full_market_analysis(niche, keywords, num_ideas=3)
                self.market_agent.display_results(analysis)
                best_idea = analysis.recommended_products[0] if analysis.recommended_products else None
                product_title = best_idea.title if best_idea else f"The Ultimate {niche.title()} Guide"
                product_price = price or (best_idea.estimated_price if best_idea else 19)
                outline = best_idea.content_outline if best_idea else [f"Chapter {i+1}" for i in range(5)]
            else:
                product_title = f"The Ultimate {niche.title()} Guide"
                product_price = price or 19
                outline = [f"Chapter {i+1}" for i in range(5)]

            job.status = "writing"

            # Phase 2: Content Writing
            console.print("\n[bold cyan]✍️  PHASE 2: Content Writing[/bold cyan]")
            if self.writer_agent:
                ebook = self.writer_agent.write_ebook(
                    title=product_title,
                    outline=outline,
                    target_pages=target_pages
                )
                content_file = self.writer_agent.save_content(ebook)
            else:
                content_file = None

            job.status = "designing"

            # Phase 3: Design
            console.print("\n[bold cyan]🎨 PHASE 3: Design[/bold cyan]")
            cover_file = None
            marketing_images = []
            if self.designer_agent:
                cover = self.designer_agent.generate_cover(product_title)
                cover_file = cover.file_path
                marketing_images = self.designer_agent.generate_marketing_images(product_title, count=3)

            job.status = "publishing"

            # Phase 4: Publishing
            console.print("\n[bold cyan]🚀 PHASE 4: Publishing[/bold cyan]")
            gumroad_url = None
            if self.publisher_agent and content_file:
                sales_copy = self.publisher_agent.generate_sales_copy(
                    product_name=product_title,
                    product_type="ebook",
                    target_audience=niche,
                    key_benefits=["Save time", "Expert knowledge", "Actionable steps"],
                    price=product_price
                )

                published = self.publisher_agent.create_gumroad_product(
                    name=product_title,
                    description=sales_copy.get("description", product_title),
                    price=product_price,
                    file_path=content_file,
                    cover_image=cover_file,
                    tags=sales_copy.get("tags", ["ebook", niche])
                )

                gumroad_url = published.url
                job.gumroad_url = gumroad_url

            job.status = "marketing"

            # Phase 5: Email Marketing
            console.print("\n[bold cyan]📧 PHASE 5: Email Marketing[/bold cyan]")
            if self.email_agent and gumroad_url:
                welcome_emails = self.email_agent.generate_welcome_sequence(product_title)
                launch_email = self.email_agent.generate_product_launch_email(
                    product_name=product_title,
                    product_price=product_price,
                    product_url=gumroad_url
                )
                self.email_agent.save_campaigns()
                console.print(f"   ✅ Created {len(welcome_emails)} welcome emails + 1 launch email")

            # Phase 6: Social Media
            console.print("\n[bold cyan]📱 PHASE 6: Social Media[/bold cyan]")
            if self.social_agent and gumroad_url:
                social_posts = self.social_agent.generate_product_launch_posts(
                    product_name=product_title,
                    product_price=product_price,
                    product_url=gumroad_url,
                    key_benefits=["Save time", "Expert knowledge", "Actionable steps"]
                )
                self.social_agent.save_posts()
                console.print(f"   ✅ Created {len(social_posts)} social media posts")

            # Phase 7: Analytics Setup
            console.print("\n[bold cyan]📈 PHASE 7: Analytics Setup[/bold cyan]")
            if self.analytics_agent:
                dashboard_data = self.analytics_agent.get_dashboard_data()
                console.print(f"   ✅ Dashboard data ready")

            job.status = "completed"
            job.completed_at = datetime.now().isoformat()
            job.product_data = {
                "title": product_title,
                "price": product_price,
                "content_file": content_file,
                "cover_file": cover_file,
                "marketing_images": [img.file_path for img in marketing_images if img.file_path],
                "gumroad_url": gumroad_url
            }

            console.print(Panel(
                f"[bold green]✅ Full Pipeline Complete![/bold green]\n"
                f"Product: {product_title}\n"
                f"Price: ${product_price}\n"
                f"Gumroad: {gumroad_url or \'N/A\'}\n"
                f"Marketing: Email + Social Ready",
                border_style="green"
            ))

        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            console.print(f"[bold red]❌ Production failed: {str(e)}[/bold red]")

        return job

    # ═══════════════════════════════════════════════════════
    # إنتاج سريع لأنواع أخرى
    # ═══════════════════════════════════════════════════════

    def produce_template(self, template_name: str, template_type: str, platform: str = "notion") -> ProductionJob:
        """إنتاج قالب أعمال"""
        job_id = f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}""
        job = ProductionJob(job_id=job_id, niche=template_name, product_type="template", status="writing", created_at=datetime.now().isoformat())
        self.jobs.append(job)

        try:
            if self.business_agent:
                if template_type == "CRM":
                    template = self.business_agent.generate_crm_template(template_name, platform)
                elif template_type == "Marketing":
                    template = self.business_agent.generate_marketing_kit(template_name)
                else:
                    template = self.business_agent.generate_financial_tracker(template_name)

                template_file = self.business_agent.save_template(template)

                if self.publisher_agent:
                    sales_copy = self.publisher_agent.generate_sales_copy(
                        product_name=template.name, product_type="template",
                        target_audience="professionals", key_benefits=["Save time", "Organized workflow", "Proven system"], price=19
                    )
                    published = self.publisher_agent.create_gumroad_product(
                        name=template.name, description=sales_copy.get("description", template.description),
                        price=19, file_path=template_file, tags=sales_copy.get("tags", ["template", platform])
                    )
                    job.gumroad_url = published.url

                job.status = "completed"
                job.product_data = {"template_file": template_file}
        except Exception as e:
            job.status = "failed"; job.error = str(e)

        return job

    def produce_software_tool(self, tool_name: str, purpose: str, language: str = "python") -> ProductionJob:
        """إنتاج أداة برمجية"""
        job_id = f"software_{datetime.now().strftime('%Y%m%d_%H%M%S')}""
        job = ProductionJob(job_id=job_id, niche=tool_name, product_type="software", status="coding", created_at=datetime.now().isoformat())
        self.jobs.append(job)

        try:
            if self.code_agent:
                tool = self.code_agent.generate_tool(tool_name, purpose, language)
                tool_dir = self.code_agent.save_product(tool)

                import shutil
                zip_path = f"{tool_dir}.zip"
                shutil.make_archive(tool_dir, "zip", tool_dir)

                if self.publisher_agent:
                    sales_copy = self.publisher_agent.generate_sales_copy(
                        product_name=tool_name, product_type="software",
                        target_audience="developers", key_benefits=["Automates tasks", "Saves hours", "Easy to use"], price=29
                    )
                    published = self.publisher_agent.create_gumroad_product(
                        name=tool_name, description=sales_copy.get("description", purpose),
                        price=29, file_path=zip_path, tags=sales_copy.get("tags", ["software", "tool", "automation"])
                    )
                    job.gumroad_url = published.url

                job.status = "completed"
                job.product_data = {"tool_dir": tool_dir, "zip_path": zip_path}
        except Exception as e:
            job.status = "failed"; job.error = str(e)

        return job

    def produce_fitness_plan(self, goal: str, level: str = "beginner", duration_weeks: int = 4) -> ProductionJob:
        """إنتاج خطة لياقة"""
        job_id = f"fitness_{datetime.now().strftime('%Y%m%d_%H%M%S')}""
        job = ProductionJob(job_id=job_id, niche=goal, product_type="fitness", status="creating", created_at=datetime.now().isoformat())
        self.jobs.append(job)

        try:
            if self.health_agent:
                plan = self.health_agent.generate_workout_plan(goal, level, duration_weeks)
                plan_file = self.health_agent.save_plan(plan)

                if self.publisher_agent:
                    sales_copy = self.publisher_agent.generate_sales_copy(
                        product_name=plan.name, product_type="fitness_plan",
                        target_audience=f"{level} fitness enthusiasts", key_benefits=["Structured plan", "Proven results", "Easy to follow"], price=17
                    )
                    published = self.publisher_agent.create_gumroad_product(
                        name=plan.name, description=sales_copy.get("description", plan.name),
                        price=17, file_path=plan_file, tags=sales_copy.get("tags", ["fitness", "workout", "health"])
                    )
                    job.gumroad_url = published.url

                job.status = "completed"
                job.product_data = {"plan_file": plan_file}
        except Exception as e:
            job.status = "failed"; job.error = str(e)

        return job

    # ═══════════════════════════════════════════════════════
    # التقارير والإحصائيات
    # ═══════════════════════════════════════════════════════

    def get_revenue_report(self, days: int = 30) -> Dict:
        """تقرير الإيرادات"""
        if self.payment_agent:
            return self.payment_agent.get_revenue_report(days)
        return {"error": "Payment agent not available"}

    def get_dashboard_data(self) -> Dict:
        """بيانات لوحة التحكم"""
        if self.analytics_agent:
            return self.analytics_agent.get_dashboard_data()
        return {}

    def get_jobs_report(self):
        """عرض تقرير المهام"""
        console.print("\n[bold cyan]📋 Production Jobs Report[/bold cyan]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Job ID", style="dim")
        table.add_column("Type")
        table.add_column("Niche")
        table.add_column("Status")
        table.add_column("URL")

        for job in self.jobs:
            status_color = {"completed": "green", "failed": "red", "pending": "yellow",
                          "researching": "blue", "writing": "cyan", "designing": "magenta",
                          "publishing": "green", "marketing": "yellow"}.get(job.status, "white")

            table.add_row(
                job.job_id[:20], job.product_type, job.niche[:30],
                f"[{status_color}]{job.status}[/{status_color}]",
                job.gumroad_url[:40] if job.gumroad_url else "-"
            )

        console.print(table)


if __name__ == "__main__":
    orchestrator = DigitalFactoryOrchestrator()
    job = orchestrator.produce_ebook(
        niche="productivity for remote workers",
        keywords=["remote work", "productivity", "time management"],
        target_pages=30
    )
    orchestrator.get_jobs_report()
