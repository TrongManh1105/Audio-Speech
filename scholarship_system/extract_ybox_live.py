from parse_ybox_state import initial_state
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

posts = initial_state.get('app', {}).get('initialPosts', {})

for group_name in ['NewestPosts', 'HighlightPosts', 'SelectivePosts']:
    group_posts = posts.get(group_name, [])
    print(f"\n=== {group_name} ({len(group_posts)} bài viết) ===")
    for p in group_posts[:5]:
        title = p.get('title') or p.get('name')
        slug = p.get('slug') or p.get('_id')
        desc = p.get('description') or p.get('excerpt') or p.get('summary') or ""
        created = p.get('createdAt') or p.get('publishDate')
        print(f"  * {title}")
        print(f"    Link: https://ybox.vn/hoc-bong/{slug}")
        if desc:
            print(f"    Tóm tắt: {desc[:100]}...")
