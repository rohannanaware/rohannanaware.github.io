---
title: "Hello, world: how posts work on this site"
subtitle: A sample post you can delete once you've added real ones.
date: 2026-11-01
categories: [thoughts]
---
This is a sample post. Every post is a Markdown file in `_posts/`, named `YYYY-MM-DD-short-title.md`, with a small block of front matter at the top.

## Front matter

```yaml
---
title: "Sunrise at the ridge"
subtitle: One line shown under the title (optional)
date: 2026-11-01
categories: [hiking]        # one of the section keys in _data/sections.yml
cover: /assets/images/hiking/ridge/cover.jpg   # optional card and header image
---
```

The first category decides which section page the post appears on, and also its URL (`/hiking/sunrise-at-the-ridge/`).

## Images

Put images under `assets/images/` and reference them with a normal Markdown image. A folder per post keeps things tidy:

```markdown
![Clouds below the ridge](/assets/images/hiking/ridge/clouds.jpg)
```

## Code

```python
import pandas as pd

df = pd.read_csv("trail_log.csv")
print(df.groupby("year")["distance_km"].sum())
```

Delete this file when you're ready to publish real content.
