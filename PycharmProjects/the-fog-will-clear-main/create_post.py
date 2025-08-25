from app import app, db, Post

def create_blog_post():
    with app.app_context():
        post = Post(
            title="Smoke Free. Fog Clear. Life Back.",
            content="""
Three weeks ago, I made a choice.

I put down the cigarette — and picked up my life.

The fog that once clouded my mornings is starting to lift. I’m breathing easier. I’m thinking clearer. My senses are waking up again, one by one. The cravings still come, but each time I say no, I say yes to something bigger: my freedom.

I’ve stopped burning away my energy. My money. My time.

This is more than quitting smoking. This is reclaiming *me*.

To anyone else fighting the urge — I see you. Keep going. The fog will clear.

And when it does, you'll realize: the view was worth it.
            """,
            likes=0
        )
        db.session.add(post)
        db.session.commit()
        print(f"Created post with ID: {post.id}")

if __name__ == "__main__":
    create_blog_post()
