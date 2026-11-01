# My GitHub Pages site

A simple [Jekyll](https://jekyllrb.com/) site that GitHub builds and hosts for free. No build step on your side: write Markdown, push, done.

Sections: Hiking · Travel · Data Science · Coding · Linux · Raspberry Pi · Thoughts · Journals

## 1. Publish it

1. On GitHub, create a **public** repo named exactly `YOUR-USERNAME.github.io` (this gives you `https://YOUR-USERNAME.github.io`).
2. In `_config.yml`, replace `YOUR-USERNAME` (in `url` and `github_username`) and set `title`, `tagline`, `author`.
3. Push this folder to the repo's `main` branch:
   ```bash
   cd site
   git init -b main
   git add .
   git commit -m "Initial site"
   git remote add origin git@github.com:YOUR-USERNAME/YOUR-USERNAME.github.io.git
   git push -u origin main
   ```
4. In the repo: **Settings → Pages → Build and deployment → Source: Deploy from a branch → `main` / `(root)`**. After a minute or two the site is live.

Already have a repo you'd rather use? Pages also works from any repo, but then the address is `https://YOUR-USERNAME.github.io/REPO/`; set `baseurl: "/REPO"` in `_config.yml` and prefix image paths in posts accordingly. A `YOUR-USERNAME.github.io` repo avoids that.

## 2. Preview locally (optional)

Needs Ruby. Pushing to GitHub also works as a preview, just slower.

```bash
bundle install
bundle exec jekyll serve      # http://localhost:4000
```

## 3. Bring over your Medium posts

1. Request your export at <https://medium.com/me/export>. Medium emails you a zip (can take a while).
2. Run the importer (Python 3):
   ```bash
   pip install -r tools/requirements.txt
   python tools/medium_to_jekyll.py ~/Downloads/medium-export.zip --site .
   ```
3. It writes one Markdown file per post into `_posts/`, **downloads every image into `assets/images/<section>/<post>/`** (so nothing depends on Medium any more), and sets each post's first image as its cover.
4. Sections are **guessed from keywords**. Open `tools/migration_report.csv`, check the `category` column, and fix any wrong ones by editing `categories: [...]` at the top of that post. Posts that match no keywords default to `thoughts`.

Useful options: `--category hiking` (put everything in one section, handy for batches), `--no-images`, `--include-drafts`, `--overwrite`. Re-running is safe; existing posts are skipped.

Things to check after importing: embedded tweets/gists/videos come across as plain links, and a few formatting quirks (odd line breaks, escaped characters) may need a quick manual fix.

## 4. Bring over data science notebooks

For notebooks already on your GitHub, either link to the repo from a short post, or convert them so they read like posts:

```bash
pip install nbconvert
jupyter nbconvert --to markdown my_analysis.ipynb --output-dir _posts/_tmp
```

Then move the `.md` into `_posts/` as `YYYY-MM-DD-my-analysis.md`, move the generated `my_analysis_files/` images into `assets/images/data-science/my-analysis/`, fix the image paths, and add front matter:

```yaml
---
title: "My analysis"
date: 2026-11-01
categories: [data-science]
---
```

## 5. Writing new posts

Create `_posts/YYYY-MM-DD-short-title.md`:

```yaml
---
title: "Sunrise at the ridge"
subtitle: Optional one-liner
date: 2026-11-01
categories: [hiking]
cover: /assets/images/hiking/ridge/cover.jpg   # optional
---
Text here. Images: ![caption](/assets/images/hiking/ridge/clouds.jpg)
```

`_posts/2026-11-01-hello-world.md` is a sample showing this; delete it when you have real posts.

Tips for photo-heavy posts: resize images to about 1600 px wide before adding them (a repo has a soft 1 GB limit and big originals slow the site down).

## 6. Customising

| What | Where |
| --- | --- |
| Add, rename or reorder sections | `_data/sections.yml`, plus a folder with an `index.md` copied from an existing section |
| Colours, fonts, spacing | top of `assets/css/style.css` (the `:root` variables) |
| Home page intro text | `index.md` |
| About page | `about.md` |
| Page structure | `_layouts/` and `_includes/` |

Light and dark mode follow the visitor's system setting. An RSS feed is generated at `/feed.xml`.

## Layout

```
_config.yml          site settings
_data/sections.yml   list of sections (drives nav, home tiles, section pages)
_layouts/            default, home, section, post, page
_includes/           post-list card grid
_posts/              all posts, any section
assets/css/          stylesheet
assets/images/       images, organised by section/post
hiking/ travel/ ...  one index.md per section
tools/               Medium importer
```
