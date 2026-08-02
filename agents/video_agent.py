"""
🎬 Video Agent
===============
وكيل الفيديو - ينتج سكريبتات الفيديو والمحتوى المرئي
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
class VideoScript:
    """سكريبت فيديو"""
    title: str
    duration_minutes: int
    scenes: List[Dict]
    narration: str
    visual_notes: str
    b_roll_suggestions: List[str]
    music_mood: str


class VideoAgent:
    """
    🎬 وكيل الفيديو

    ينتج:
    - سكريبتات فيديو تعليمية
    - محتوى رقمي
    - وصف مشاهد (storyboard)
    - اقتراحات B-roll
    """

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)
        self.client = OpenAI(api_key=self.config["api_keys"]["openai"])
        console.print(Panel(
            "[bold red]🎬 Video Agent Initialized[/bold red]",
            border_style="red"
        ))

    def generate_video_script(
        self,
        topic: str,
        target_duration: int = 10,
        style: str = "educational",
        audience: str = "general"
    ) -> VideoScript:
        """توليد سكريبت فيديو كامل"""
        console.print(f"
[bold yellow]🎬 Generating Video Script: {topic}...[/bold yellow]")

        prompt = f"""
        Create a detailed video script for an educational video.

        Topic: {topic}
        Target Duration: {target_duration} minutes
        Style: {style}
        Target Audience: {audience}

        Provide the script in this JSON format:
        {{
            "title": "Video Title",
            "scenes": [
                {{
                    "scene_number": 1,
                    "timestamp": "0:00-1:30",
                    "narration": "What the narrator says...",
                    "visual_description": "What appears on screen...",
                    "b_roll": "Suggested B-roll footage...",
                    "key_point": "Main takeaway"
                }}
            ],
            "full_narration": "Complete narration text...",
            "visual_style_notes": "Overall visual direction...",
            "b_roll_list": ["suggestion1", "suggestion2"],
            "music_mood": "upbeat/calm/inspirational"
        }}

        Make it engaging, professional, and actionable.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000
        )

        try:
            import json
            content_text = response.choices[0].message.content
            json_start = content_text.find("{")
            json_end = content_text.rfind("}") + 1
            data = json.loads(content_text[json_start:json_end])

            script = VideoScript(
                title=data.get("title", topic),
                duration_minutes=target_duration,
                scenes=data.get("scenes", []),
                narration=data.get("full_narration", ""),
                visual_notes=data.get("visual_style_notes", ""),
                b_roll_suggestions=data.get("b_roll_list", []),
                music_mood=data.get("music_mood", "calm")
            )

            console.print(f"   ✅ Script generated: {len(script.scenes)} scenes")
            return script

        except Exception as e:
            console.print(f"   ❌ Error: {str(e)}")
            return VideoScript(title=topic, duration_minutes=target_duration, scenes=[], narration="", visual_notes="", b_roll_suggestions=[], music_mood="calm")

    def generate_storyboard(
        self,
        script: VideoScript
    ) -> List[Dict]:
        """توليد وصف مشاهد تفصيلي (storyboard)"""
        console.print(f"
[bold yellow]🎨 Generating Storyboard for: {script.title}...[/bold yellow]")

        storyboard = []

        for scene in script.scenes:
            prompt = f"""
            Create a detailed image generation prompt for this video scene:

            Scene: {scene.get("scene_number", 1)}
            Visual: {scene.get("visual_description", "")}

            Write a DALL-E 3 prompt (50-80 words) that captures this scene visually.
            Make it cinematic, professional, and suitable for video production.
            """

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=300
            )

            image_prompt = response.choices[0].message.content

            storyboard.append({
                "scene": scene.get("scene_number", 1),
                "timestamp": scene.get("timestamp", ""),
                "narration": scene.get("narration", ""),
                "image_prompt": image_prompt,
                "visual_description": scene.get("visual_description", "")
            })

        console.print(f"   ✅ Storyboard complete: {len(storyboard)} frames")
        return storyboard

    def save_script(self, script: VideoScript, storyboard: List[Dict], output_dir: str = "products/video") -> str:
        """حفظ السكريبت والستوريبورد"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/video_script_{timestamp}.md"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {script.title}

")
            f.write(f"**Duration:** {script.duration_minutes} minutes
")
            f.write(f"**Music Mood:** {script.music_mood}

")
            f.write(f"## Full Narration

{script.narration}

")
            f.write(f"## Visual Style Notes

{script.visual_notes}

")
            f.write("## Scenes

")

            for scene in script.scenes:
                f.write(f"### Scene {scene.get('scene_number', 1)}
")
                f.write(f"**Timestamp:** {scene.get('timestamp', '')}
")
                f.write(f"**Narration:** {scene.get('narration', '')}
")
                f.write(f"**Visual:** {scene.get('visual_description', '')}
")
                f.write(f"**B-Roll:** {scene.get('b_roll', '')}
")
                f.write(f"**Key Point:** {scene.get('key_point', '')}

")

            f.write("## Storyboard

")
            for frame in storyboard:
                f.write(f"### Frame {frame['scene']}
")
                f.write(f"**Timestamp:** {frame['timestamp']}
")
                f.write(f"**Image Prompt:** {frame['image_prompt']}

")

        console.print(f"[bold blue]💾 Video script saved: {filename}[/bold blue]")
        return filename


if __name__ == "__main__":
    agent = VideoAgent()
    script = agent.generate_video_script("How to Build a Morning Routine", 5)
    storyboard = agent.generate_storyboard(script)
    agent.save_script(script, storyboard)
