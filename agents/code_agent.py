"""
💻 Code Agent
==============
وكيل البرمجة - يبني التطبيقات والأدوات والإضافات
"""

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
class SoftwareProduct:
    """منتج برمجي"""
    name: str
    description: str
    language: str
    files: List[Dict]
    readme: str
    setup_instructions: str
    file_path: Optional[str] = None


class CodeAgent:
    """
    💻 وكيل البرمجة

    ينتج:
    - تطبيقات Python
    - إضافات متصفح
    - APIs
    - أدوات أتمتة
    - سكريبتات مفيدة
    """

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)
        self.client = OpenAI(api_key=self.config["api_keys"]["openai"])
        console.print(Panel(
            "[bold blue]💻 Code Agent Initialized[/bold blue]",
            border_style="blue"
        ))

    def generate_tool(
        self,
        tool_name: str,
        purpose: str,
        language: str = "python",
        complexity: str = "medium"
    ) -> SoftwareProduct:
        """توليد أداة برمجية كاملة"""
        console.print(f"
[bold yellow]💻 Generating Tool: {tool_name}...[/bold yellow]")

        prompt = f"""
        Create a complete, production-ready software tool.

        Tool Name: {tool_name}
        Purpose: {purpose}
        Language: {language}
        Complexity: {complexity}

        Provide the complete code in this format:

        FILE: main.py
        ```python
        # Complete code here
        ```

        FILE: requirements.txt
        ```
        # Dependencies
        ```

        FILE: README.md
        ```markdown
        # Complete README
        ```

        FILE: config.json
        ```json
        # Configuration
        ```

        Make sure:
        - Code is clean and well-commented
        - Includes error handling
        - Has a CLI interface
        - Includes setup instructions
        - Is ready to sell as a digital product
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000
        )

        code_content = response.choices[0].message.content

        # Parse files from the response
        files = self._parse_files(code_content)

        # Generate README if not included
        readme = files.get("README.md", f"# {tool_name}

{purpose}
")

        product = SoftwareProduct(
            name=tool_name,
            description=purpose,
            language=language,
            files=[{"name": k, "content": v} for k, v in files.items()],
            readme=readme,
            setup_instructions="See README.md for setup instructions."
        )

        console.print(f"   ✅ Tool generated: {len(files)} files")
        return product

    def _parse_files(self, content: str) -> Dict[str, str]:
        """Parse files from AI response"""
        files = {}
        lines = content.split("
")
        current_file = None
        current_content = []
        in_code_block = False

        for line in lines:
            if line.startswith("FILE: "):
                if current_file and current_content:
                    files[current_file] = "
".join(current_content).strip()
                current_file = line.replace("FILE: ", "").strip()
                current_content = []
            elif line.startswith("```"):
                in_code_block = not in_code_block
                if not in_code_block and current_file:
                    continue
            elif current_file and in_code_block:
                current_content.append(line)

        if current_file and current_content:
            files[current_file] = "
".join(current_content).strip()

        return files

    def generate_api(
        self,
        api_name: str,
        endpoints: List[str],
        framework: str = "fastapi"
    ) -> SoftwareProduct:
        """توليد API جاهز"""
        console.print(f"
[bold yellow]🔌 Generating API: {api_name}...[/bold yellow]")

        prompt = f"""
        Create a complete {framework} API.

        API Name: {api_name}
        Endpoints: {endpoints}

        Include:
        - Main application file
        - Models/schemas
        - Authentication
        - Documentation
        - Tests
        - Deployment guide
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000
        )

        code_content = response.choices[0].message.content
        files = self._parse_files(code_content)

        return SoftwareProduct(
            name=api_name,
            description=f"{framework} API with {len(endpoints)} endpoints",
            language="python",
            files=[{"name": k, "content": v} for k, v in files.items()],
            readme=files.get("README.md", ""),
            setup_instructions="pip install -r requirements.txt && uvicorn main:app"
        )

    def save_product(self, product: SoftwareProduct, output_dir: str = "products/software") -> str:
        """حفظ المنتج البرمجي"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        product_dir = f"{output_dir}/{product.name.replace(' ', '_')}_{timestamp}"
        os.makedirs(product_dir, exist_ok=True)

        for file_info in product.files:
            filepath = os.path.join(product_dir, file_info["name"])
            os.makedirs(os.path.dirname(filepath) if "/" in file_info["name"] else product_dir, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(file_info["content"])

        product.file_path = product_dir
        console.print(f"[bold blue]💾 Software saved: {product_dir}[/bold blue]")
        return product_dir


if __name__ == "__main__":
    agent = CodeAgent()
    tool = agent.generate_tool("Social Media Scheduler", "Schedule posts across platforms", "python")
    agent.save_product(tool)
