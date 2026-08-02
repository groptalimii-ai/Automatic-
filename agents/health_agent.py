"""
💪 Health & Fitness Agent
==========================
وكيل الصحة - يصمم برامج تمارين وخطط غذائية
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
class FitnessPlan:
    """خطة لياقة"""
    name: str
    plan_type: str  # workout, nutrition, combined
    duration_weeks: int
    target_audience: str
    schedule: List[Dict]
    meals: List[Dict]
    guidelines: str
    file_path: Optional[str] = None


class HealthAgent:
    """
    💪 وكيل الصحة واللياقة

    ينتج:
    - برامج تمارين
    - خطط غذائية
    - جداول تدريب
    - محتوى متخصص
    """

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)
        self.client = OpenAI(api_key=self.config["api_keys"]["openai"])
        console.print(Panel(
            "[bold green]💪 Health & Fitness Agent Initialized[/bold green]",
            border_style="green"
        ))

    def generate_workout_plan(
        self,
        goal: str,
        fitness_level: str = "beginner",
        duration_weeks: int = 4,
        equipment: str = "minimal",
        sessions_per_week: int = 4
    ) -> FitnessPlan:
        """توليد خطة تمارين"""
        console.print(f"
[bold yellow]💪 Generating Workout Plan: {goal}...[/bold yellow]")

        prompt = f"""
        Create a detailed {duration_weeks}-week workout plan.

        Goal: {goal}
        Fitness Level: {fitness_level}
        Equipment: {equipment}
        Sessions per week: {sessions_per_week}

        Provide in JSON format:
        {{
            "plan_name": "Name",
            "overview": "Plan overview",
            "weeks": [
                {{
                    "week": 1,
                    "focus": "Focus area",
                    "sessions": [
                        {{
                            "day": "Monday",
                            "workout_type": "Strength/Cardio/etc",
                            "exercises": [
                                {{
                                    "name": "Exercise name",
                                    "sets": 3,
                                    "reps": "10-12",
                                    "rest": "60s",
                                    "notes": "Form tips"
                                }}
                            ],
                            "duration": "45 min",
                            "intensity": "Medium"
                        }}
                    ]
                }}
            ],
            "progression_rules": "How to progress",
            "safety_notes": "Important safety information"
        }}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=4000
        )

        try:
            content_text = response.choices[0].message.content
            json_start = content_text.find("{")
            json_end = content_text.rfind("}") + 1
            plan_data = json.loads(content_text[json_start:json_end])
        except:
            plan_data = {"plan_name": f"{goal} Plan", "weeks": []}

        schedule = []
        for week in plan_data.get("weeks", []):
            for session in week.get("sessions", []):
                schedule.append({
                    "week": week.get("week", 1),
                    "day": session.get("day", ""),
                    "type": session.get("workout_type", ""),
                    "exercises": session.get("exercises", []),
                    "duration": session.get("duration", "45 min")
                })

        plan = FitnessPlan(
            name=plan_data.get("plan_name", f"{goal} Workout Plan"),
            plan_type="workout",
            duration_weeks=duration_weeks,
            target_audience=f"{fitness_level} level",
            schedule=schedule,
            meals=[],
            guidelines=plan_data.get("safety_notes", "")
        )

        console.print(f"   ✅ Workout plan generated: {len(schedule)} sessions over {duration_weeks} weeks")
        return plan

    def generate_meal_plan(
        self,
        diet_type: str,
        calories: int = 2000,
        restrictions: List[str] = None,
        duration_days: int = 7
    ) -> FitnessPlan:
        """توليد خطة غذائية"""
        console.print(f"
[bold yellow]🥗 Generating Meal Plan: {diet_type}...[/bold yellow]")

        if restrictions is None:
            restrictions = []

        prompt = f"""
        Create a detailed {duration_days}-day meal plan.

        Diet Type: {diet_type}
        Daily Calories: {calories}
        Restrictions: {restrictions}

        Provide each day with:
        - Breakfast (with macros)
        - Lunch (with macros)
        - Dinner (with macros)
        - Snacks (with macros)
        - Daily totals
        - Prep tips

        Make it practical and delicious.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=4000
        )

        content = response.choices[0].message.content

        # Parse meals
        meals = []
        days = content.split("Day")[1:] if "Day" in content else [content]

        for day_content in days[:duration_days]:
            meals.append({
                "day": day_content.split("
")[0].strip() if day_content.split("
") else "Day",
                "content": day_content[:500]
            })

        return FitnessPlan(
            name=f"{diet_type} Meal Plan ({calories} cal)",
            plan_type="nutrition",
            duration_weeks=duration_days // 7,
            target_audience=f"{diet_type} diet followers",
            schedule=[],
            meals=meals,
            guidelines=f"Daily target: {calories} calories. Restrictions: {', '.join(restrictions)}"
        )

    def save_plan(self, plan: FitnessPlan, output_dir: str = "products/health") -> str:
        """حفظ الخطة"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = plan.name.replace(" ", "_").replace("/", "_")
        filename = f"{output_dir}/{safe_name}_{timestamp}.md"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {plan.name}

")
            f.write(f"**Type:** {plan.plan_type}
")
            f.write(f"**Duration:** {plan.duration_weeks} weeks
")
            f.write(f"**Target:** {plan.target_audience}

")

            if plan.schedule:
                f.write("## Workout Schedule

")
                for session in plan.schedule:
                    f.write(f"### Week {session['week']} - {session['day']}
")
                    f.write(f"**Type:** {session['type']} | **Duration:** {session['duration']}

")
                    for ex in session.get("exercises", []):
                        f.write(f"- **{ex.get('name', '')}**: {ex.get('sets', 3)} sets x {ex.get('reps', '')} reps ({ex.get('rest', '')} rest)
")
                    f.write("
")

            if plan.meals:
                f.write("## Meal Plan

")
                for meal in plan.meals:
                    f.write(f"### {meal['day']}
")
                    f.write(f"{meal['content']}

")

            f.write("## Guidelines

")
            f.write(plan.guidelines)

        plan.file_path = filename
        console.print(f"[bold blue]💾 Fitness plan saved: {filename}[/bold blue]")
        return filename


if __name__ == "__main__":
    agent = HealthAgent()
    workout = agent.generate_workout_plan("Build Muscle", "intermediate", 4)
    agent.save_plan(workout)
