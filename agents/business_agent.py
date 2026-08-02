"""
📊 Business Agent
==================
وكيل الأعمال - يصمم قوالب CRM وأنظمة التسويق والأدوات المالية
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

import yaml
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

console = Console()


@dataclass
class BusinessTemplate:
    """قالب أعمال"""
    name: str
    template_type: str  # CRM, Marketing, Finance, Project Management
    description: str
    structure: Dict
    instructions: str
    examples: List[str]
    file_path: Optional[str] = None


class BusinessAgent:
    """
    📊 وكيل الأعمال

    ينتج:
    - قوالب CRM (Notion, Airtable, Excel)
    - أنظمة تسويق
    - أدوات مالية
    - خطط استراتيجية
    """

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)
        self.client = OpenAI(api_key=self.config["api_keys"]["openai"])
        console.print(Panel(
            "[bold cyan]📊 Business Agent Initialized[/bold cyan]",
            border_style="cyan"
        ))

    def generate_crm_template(
        self,
        business_type: str,
        platform: str = "notion",
        features: List[str] = None
    ) -> BusinessTemplate:
        """توليد قالب CRM"""
        console.print(f"
[bold yellow]📊 Generating CRM Template for {business_type}...[/bold yellow]")

        if features is None:
            features = ["contacts", "deals", "tasks", "pipeline"]

        prompt = f"""
        Create a detailed CRM template structure for:
        Business Type: {business_type}
        Platform: {platform}
        Features: {features}

        Provide the template structure in JSON format:
        {{
            "template_name": "Name",
            "description": "Description",
            "databases": [
                {{
                    "name": "Contacts",
                    "properties": ["Name", "Email", "Status", "Source"],
                    "views": ["Table", "Board", "Calendar"]
                }}
            ],
            "automations": ["Automation 1", "Automation 2"],
            "formulas": ["Formula 1", "Formula 2"],
            "setup_steps": ["Step 1", "Step 2"]
        }}

        Also provide detailed setup instructions.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=3000
        )

        try:
            content_text = response.choices[0].message.content
            json_start = content_text.find("{")
            json_end = content_text.rfind("}") + 1
            structure = json.loads(content_text[json_start:json_end])
        except:
            structure = {"template_name": f"{business_type} CRM", "databases": []}

        template = BusinessTemplate(
            name=f"{business_type} CRM System",
            template_type="CRM",
            description=f"Complete CRM template for {business_type} businesses",
            structure=structure,
            instructions="See setup guide in the template files.",
            examples=["Contact management", "Deal tracking", "Task automation"]
        )

        console.print(f"   ✅ CRM template generated: {len(structure.get('databases', []))} databases")
        return template

    def generate_marketing_kit(
        self,
        niche: str,
        channels: List[str] = None
    ) -> BusinessTemplate:
        """توليد حزمة تسويق"""
        console.print(f"
[bold yellow]📈 Generating Marketing Kit for {niche}...[/bold yellow]")

        if channels is None:
            channels = ["email", "social_media", "content"]

        prompt = f"""
        Create a complete marketing system template for:
        Niche: {niche}
        Channels: {channels}

        Include:
        1. Content calendar template
        2. Email sequences (5 emails)
        3. Social media post templates (20 posts)
        4. Analytics dashboard structure
        5. Campaign tracking sheets

        Provide in structured format.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000
        )

        content = response.choices[0].message.content

        # Parse email sequences
        emails = []
        posts = []
        lines = content.split("
")
        current_section = None

        for line in lines:
            if "Email" in line and ":" in line:
                current_section = "email"
            elif "Post" in line and ":" in line:
                current_section = "post"
            elif current_section == "email" and line.strip():
                emails.append(line.strip())
            elif current_section == "post" and line.strip():
                posts.append(line.strip())

        template = BusinessTemplate(
            name=f"{niche} Marketing Kit",
            template_type="Marketing",
            description=f"Complete marketing system for {niche}",
            structure={
                "content_calendar": "12-month calendar",
                "email_sequences": emails[:5],
                "social_posts": posts[:20],
                "analytics_dashboard": "KPI tracking"
            },
            instructions=content[:500],
            examples=["Launch campaign", "Weekly newsletter", "Social media calendar"]
        )

        console.print(f"   ✅ Marketing kit generated: {len(emails)} emails, {len(posts)} posts")
        return template

    def generate_financial_tracker(
        self,
        purpose: str = "personal",
        complexity: str = "medium"
    ) -> BusinessTemplate:
        """توليد أداة تتبع مالي"""
        console.print(f"
[bold yellow]💰 Generating Financial Tracker...[/bold yellow]")

        prompt = f"""
        Create a comprehensive financial tracking template.

        Purpose: {purpose}
        Complexity: {complexity}

        Include:
        - Income tracking
        - Expense categories
        - Budget planning
        - Savings goals
        - Investment tracker
        - Monthly reports
        - Formulas and calculations

        Provide as structured template description.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=3000
        )

        content = response.choices[0].message.content

        return BusinessTemplate(
            name=f"{purpose.title()} Financial Tracker",
            template_type="Finance",
            description=f"Complete financial tracking system for {purpose} use",
            structure={"sheets": ["Income", "Expenses", "Budget", "Savings", "Investments"]},
            instructions=content,
            examples=["Monthly budget", "Expense analysis", "Savings goals"]
        )

    def save_template(self, template: BusinessTemplate, output_dir: str = "products/business") -> str:
        """حفظ القالب"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = template.name.replace(" ", "_").replace("/", "_")
        filename = f"{output_dir}/{safe_name}_{timestamp}.json"

        data = {
            "name": template.name,
            "type": template.template_type,
            "description": template.description,
            "structure": template.structure,
            "instructions": template.instructions,
            "examples": template.examples
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Also save instructions as markdown
        md_filename = filename.replace(".json", ".md")
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(f"# {template.name}

")
            f.write(f"**Type:** {template.template_type}

")
            f.write(f"**Description:** {template.description}

")
            f.write("## Instructions

")
            f.write(template.instructions)
            f.write("

## Examples

")
            for ex in template.examples:
                f.write(f"- {ex}
")

        template.file_path = filename
        console.print(f"[bold blue]💾 Business template saved: {filename}[/bold blue]")
        return filename


if __name__ == "__main__":
    agent = BusinessAgent()
    crm = agent.generate_crm_template("Freelance Design Agency")
    agent.save_template(crm)
