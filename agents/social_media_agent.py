        - Hook (first line that grabs attention)
        - Format (carousel, reel, thread, etc.)
        - Why it works (psychology)
        - Estimated engagement

        Focus on formats that work in 2026.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=2000
        )

        try:
            content = response.choices[0].message.content
            json_start = content.find("[")
            json_end = content.rfind("]") + 1
            ideas = json.loads(content[json_start:json_end])
            console.print(f"   ✅ Generated {len(ideas)} viral ideas")
            return ideas
        except:
            return [{"hook": f"The truth about {niche}", "format": "carousel", "why": "curiosity gap"}]

    def save_posts(self, output_dir: str = "products/social"):
        """حفظ المنشورات"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for post in self.posts:
            filename = f"{output_dir}/{post.platform}_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"Platform: {post.platform}\n")
                f.write(f"Status: {post.status}\n")
                f.write(f"Scheduled: {post.scheduled_time}\n\n")
                f.write(post.content)
                f.write(f"\n\nHashtags: {', '.join(post.hashtags)}")
                if post.image_prompt:
                    f.write(f"\n\nImage Prompt: {post.image_prompt}")

        console.print(f"   ✅ Saved {len(self.posts)} posts to {output_dir}")


if __name__ == "__main__":
    agent = SocialMediaAgent()
    posts = agent.generate_product_launch_posts(
        "Productivity Toolkit",
        27,
        "https://gumroad.com/l/toolkit",
        ["Save 5 hours/week", "Better focus", "Less stress"]
    )
    agent.save_posts()
