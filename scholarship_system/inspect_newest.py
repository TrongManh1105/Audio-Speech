from parse_ybox_state import initial_state

posts = initial_state.get('app', {}).get('initialPosts', {})
newest = posts.get('NewestPosts')
print("Type of NewestPosts:", type(newest))
if isinstance(newest, dict):
    print("Keys of NewestPosts:", list(newest.keys()))
    for k, v in newest.items():
        if isinstance(v, list):
            print(f"  {k} has {len(v)} items")
            if v:
                print("  Sample item keys:", list(v[0].keys()) if isinstance(v[0], dict) else type(v[0]))
                if isinstance(v[0], dict):
                    print("  Title:", v[0].get("title") or v[0].get("name"))
                    print("  Slug:", v[0].get("slug"))
