from app import db
from app.models import Post  # Adjust to your actual import path

smoke_free_content = """
I never thought I’d write these words — but here I am, over 3 weeks smoke free.

For years, cigarettes were my comfort, my stress-relief, my go-to. I convinced myself I needed them to cope. But deep down, I knew they were stealing more than they were giving — my health, my energy, my confidence.

One day, something just clicked. Maybe it was the way I was out of breath climbing stairs. Maybe it was how tired I felt every morning. Or maybe I just got tired of the fog — not just the smoke in the air, but the fog in my mind.

So I stopped.

The first few days were rough — cravings, mood swings, self-doubt. But then something shifted. I started breathing deeper. My skin looked better. Food tasted incredible. I started feeling again.

What’s helped me stay strong?
- Prayer and quiet moments to center myself.
- Keeping my hands busy — coding, journaling, even cleaning.
- Reminding myself that I’ve made it this far, and I’m not going back.

This blog isn’t just for me. It’s for you, if you’re trying to quit. It’s for the version of me who thought it was impossible. It’s for anyone who needs to hear this:

You’re stronger than the urge. And the fog will clear.
"""

def create_post():
    post = Post(
        title="Smoke Free. Fog Clear. Life Back.",
        content=smoke_free_content,
        likes=0
    )
    db.session.add(post)
    db.session.commit()
    print(f"Created post with ID: {post.id}")

if __name__ == "__main__":
    create_post()
