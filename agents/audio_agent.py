"""
🎵 Audio Agent
===============
وكيل الصوت - ينتج الموسيقى والمؤثرات الصوتية
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
class AudioAsset:
    """أصل صوتي"""
    audio_type: str
    title: str
    description: str
    file_path: Optional[str] = None
    url: Optional[str] = None
    duration: str = "3:00"


class AudioAgent:
    """
    🎵 وكيل الصوت

    ينتج:
    - موسيقى خلفية خالية من الحقوق
    - مؤثرات صوتية
    - تسجيلات صوتية (TTS)
    """

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)
        self.client = OpenAI(api_key=self.config["api_keys"]["openai"])
        console.print(Panel(
            "[bold yellow]🎵 Audio Agent Initialized[/bold yellow]",
            border_style="yellow"
        ))

    def generate_music_description(
        self,
        mood: str,
        genre: str,
        purpose: str = "background music"
    ) -> str:
        """توليد وصف موسيقي لأدوات AI مثل Suno/Udio"""
        console.print(f"
[bold yellow]🎵 Generating Music Description: {mood} {genre}...[/bold yellow]")

        prompt = f"""
        Create a detailed music description for AI music generation.
        Mood: {mood}
        Genre: {genre}
        Purpose: {purpose}

        Write a detailed prompt (100-150 words) that describes:
        - Instruments and sounds
        - Tempo and rhythm
        - Emotional arc
        - Suitable for royalty-free use

        Return ONLY the music description prompt.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=500
        )

        description = response.choices[0].message.content
        console.print(f"   ✅ Music description generated ({len(description)} chars)")
        return description

    def generate_voiceover(
        self,
        text: str,
        voice: str = "alloy",
        model: str = "tts-1"
    ) -> AudioAsset:
        """توليد تسجيل صوتي باستخدام OpenAI TTS"""
        console.print(f"
[bold yellow]🎙️  Generating Voiceover...[/bold yellow]")

        try:
            os.makedirs("products/audio", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"products/audio/voiceover_{timestamp}.mp3"

            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text
            )

            response.stream_to_file(filename)

            console.print(f"   ✅ Voiceover saved: {filename}")

            return AudioAsset(
                audio_type="voiceover",
                title="Voiceover Track",
                description=text[:100] + "...",
                file_path=filename
            )

        except Exception as e:
            console.print(f"   ❌ Error: {str(e)}")
            return AudioAsset(audio_type="voiceover", title="Error", description=str(e))

    def create_audio_pack(
        self,
        pack_name: str,
        tracks: List[Dict]
    ) -> List[AudioAsset]:
        """إنشاء حزمة موسيقية/صوتية"""
        console.print(f"
[bold yellow]🎵 Creating Audio Pack: {pack_name}...[/bold yellow]")

        assets = []

        for track in tracks:
            desc = self.generate_music_description(
                mood=track.get("mood", "calm"),
                genre=track.get("genre", "ambient"),
                purpose=track.get("purpose", "background")
            )

            assets.append(AudioAsset(
                audio_type="music_description",
                title=track.get("title", "Untitled"),
                description=desc,
                duration=track.get("duration", "3:00")
            ))

        # حفظ وصف الحزمة
        os.makedirs("products/audio", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = pack_name.replace(" ", "_")
        pack_file = f"products/audio/{safe_name}_{timestamp}.txt"

        with open(pack_file, "w", encoding="utf-8") as pf:
            pf.write(f"# {pack_name}

")
            for asset in assets:
                pf.write(f"## {asset.title}
")
                pf.write(f"{asset.description}

")

        console.print(f"   ✅ Audio pack descriptions saved: {pack_file}")
        return assets


if __name__ == "__main__":
    agent = AudioAgent()
    desc = agent.generate_music_description("calm", "lo-fi", "study focus")
    print(desc[:200] + "...")
