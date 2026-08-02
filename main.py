#!/usr/bin/env python3
"""
🏭 Digital Factory - Main Entry Point
=====================================
مصنع المنتجات الرقمية بالذكاء الاصطناعي

Usage:
    python main.py --mode ebook --niche "productivity"
    python main.py --mode template --name "CRM System"
    python main.py --mode software --tool "Social Scheduler"
    python main.py --mode fitness --goal "Build Muscle"
    python main.py --batch --config batch_jobs.json
"""

import argparse
import json
import sys
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from core.orchestrator import DigitalFactoryOrchestrator

console = Console()


def print_banner():
    """طباعة الشعار"""
    banner = Text()
    banner.append("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🏭  D I G I T A L   F A C T O R Y  🏭                      ║
    ║                                                               ║
    ║   AI-Powered Digital Product Manufacturing System            ║
    ║   Automate. Create. Publish. Earn.                         ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """, style="bold cyan")
    console.print(banner)


def produce_ebook(args):
    """إنتاج كتاب إلكتروني"""
    orchestrator = DigitalFactoryOrchestrator(args.config)

    keywords = args.keywords.split(",") if args.keywords else [args.niche]

    job = orchestrator.produce_ebook(
        niche=args.niche,
        keywords=keywords,
        target_pages=args.pages,
        price=args.price
    )

    return job


def produce_template(args):
    """إنتاج قالب"""
    orchestrator = DigitalFactoryOrchestrator(args.config)

    job = orchestrator.produce_template(
        template_name=args.name,
        template_type=args.type,
        platform=args.platform
    )

    return job


def produce_software(args):
    """إنتاج أداة برمجية"""
    orchestrator = DigitalFactoryOrchestrator(args.config)

    job = orchestrator.produce_software_tool(
        tool_name=args.tool,
        purpose=args.purpose,
        language=args.language
    )

    return job


def produce_fitness(args):
    """إنتاج خطة لياقة"""
    orchestrator = DigitalFactoryOrchestrator(args.config)

    job = orchestrator.produce_fitness_plan(
        goal=args.goal,
        level=args.level,
        duration_weeks=args.weeks
    )

    return job


def batch_production(args):
    """إنتاج دفعة"""
    orchestrator = DigitalFactoryOrchestrator(args.config)

    with open(args.config_file, "r", encoding="utf-8") as f:
        batch_config = json.load(f)

    jobs = []
    for item in batch_config.get("jobs", []):
        console.print(f"
[bold yellow]🔄 Processing batch job: {item.get('type', 'unknown')}[/bold yellow]")

        if item["type"] == "ebook":
            job = orchestrator.produce_ebook(
                niche=item["niche"],
                keywords=item.get("keywords", [item["niche"]]),
                target_pages=item.get("pages", 30),
                price=item.get("price")
            )
        elif item["type"] == "template":
            job = orchestrator.produce_template(
                template_name=item["name"],
                template_type=item.get("template_type", "CRM"),
                platform=item.get("platform", "notion")
            )
        elif item["type"] == "software":
            job = orchestrator.produce_software_tool(
                tool_name=item["name"],
                purpose=item["purpose"],
                language=item.get("language", "python")
            )
        elif item["type"] == "fitness":
            job = orchestrator.produce_fitness_plan(
                goal=item["goal"],
                level=item.get("level", "beginner"),
                duration_weeks=item.get("weeks", 4)
            )

        jobs.append(job)

    orchestrator.get_jobs_report()
    return jobs


def main():
    parser = argparse.ArgumentParser(
        description="🏭 Digital Factory - AI-Powered Product Manufacturing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mode ebook --niche "remote work productivity" --pages 40
  %(prog)s --mode template --name "Freelance CRM" --type CRM --platform notion
  %(prog)s --mode software --tool "Email Auto-Reply" --purpose "Automate email responses"
  %(prog)s --mode fitness --goal "Lose 10kg in 8 weeks" --level intermediate --weeks 8
  %(prog)s --batch --config batch_jobs.json
        """
    )

    parser.add_argument("--mode", choices=["ebook", "template", "software", "fitness", "batch"],
                       required=True, help="Production mode")
    parser.add_argument("--config", default="config.yaml", help="Config file path")

    # Ebook args
    parser.add_argument("--niche", help="Target niche/market")
    parser.add_argument("--keywords", help="Comma-separated keywords")
    parser.add_argument("--pages", type=int, default=30, help="Target page count")
    parser.add_argument("--price", type=float, help="Product price")

    # Template args
    parser.add_argument("--name", help="Template name")
    parser.add_argument("--type", choices=["CRM", "Marketing", "Finance"], help="Template type")
    parser.add_argument("--platform", default="notion", help="Platform (notion, airtable, excel)")

    # Software args
    parser.add_argument("--tool", help="Tool name")
    parser.add_argument("--purpose", help="Tool purpose/description")
    parser.add_argument("--language", default="python", help="Programming language")

    # Fitness args
    parser.add_argument("--goal", help="Fitness goal")
    parser.add_argument("--level", default="beginner", choices=["beginner", "intermediate", "advanced"])
    parser.add_argument("--weeks", type=int, default=4, help="Plan duration in weeks")

    # Batch args
    parser.add_argument("--config-file", help="Batch configuration JSON file")

    args = parser.parse_args()

    print_banner()

    console.print(f"
[bold]Mode:[/bold] {args.mode}")
    console.print(f"[bold]Config:[/bold] {args.config}")
    console.print(f"[bold]Started:[/bold] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
")

    try:
        if args.mode == "ebook":
            if not args.niche:
                console.print("[bold red]❌ Error: --niche is required for ebook mode[/bold red]")
                sys.exit(1)
            job = produce_ebook(args)

        elif args.mode == "template":
            if not args.name:
                console.print("[bold red]❌ Error: --name is required for template mode[/bold red]")
                sys.exit(1)
            job = produce_template(args)

        elif args.mode == "software":
            if not args.tool or not args.purpose:
                console.print("[bold red]❌ Error: --tool and --purpose are required[/bold red]")
                sys.exit(1)
            job = produce_software(args)

        elif args.mode == "fitness":
            if not args.goal:
                console.print("[bold red]❌ Error: --goal is required for fitness mode[/bold red]")
                sys.exit(1)
            job = produce_fitness(args)

        elif args.mode == "batch":
            if not args.config_file:
                console.print("[bold red]❌ Error: --config-file is required for batch mode[/bold red]")
                sys.exit(1)
            jobs = batch_production(args)

        console.print("
[bold green]✅ Production Complete![/bold green]")

    except KeyboardInterrupt:
        console.print("
[bold yellow]⚠️  Production interrupted by user[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"
[bold red]❌ Fatal Error: {str(e)}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
