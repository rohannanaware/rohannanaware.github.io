---
title: "Building a home server: apps I run and how to set them up"
subtitle: Why a wrapper like CasaOS is the easiest way in, and a method that outlives any Linux version
date: 2026-11-03
categories: [linux]
---

A home server sounds like a weekend of terminal commands, config files and forum threads. It doesn't have to be. This post covers what I run at home, how I set each app up, and why I put a wrapper like CasaOS on top of Linux instead of doing everything by hand.

I've deliberately left out commands and version numbers. They go stale within months. What stays useful is the method, so that's what this post covers.

## What I run

Four apps cover almost everything I wanted from the server: my photos, my video library, my audiobooks, and a place to keep and share files. Each replaces a paid or cloud service.

### Immich: photos and videos
- **What it does:** backs up photos and videos from phones automatically and lets you browse, search and share them, with face and object recognition.
- **Replaces:** Google Photos or iCloud Photos.
- **Where its data lives:** two places that matter, the folder holding your original photos and the app's database. Back up both. The database holds albums, faces and metadata, and without it your photos are just a pile of files.
- **Gotcha:** the project changes quickly. Read the release notes before every update, and take a backup first, since occasional releases need manual steps. Keep its database on the server's local drive rather than on a network share.

### Jellyfin: movies, shows and music
- **What it does:** streams your video and music library to TVs, phones, tablets and browsers, fetching posters and descriptions automatically.
- **Replaces:** Netflix-style subscriptions for the things you already own, and paid media servers.
- **Where its data lives:** your media in plain folders, kept separate from the app's own settings. Give Jellyfin read-only access to the media so it can never alter it.
- **Gotcha:** metadata matching depends on folder and file names. Follow the naming convention in its documentation, one folder per movie or show, and most "wrong poster" problems disappear. If you want smooth playback on weak devices, check that hardware video decoding is working on your server.

### Audiobookshelf: audiobooks and podcasts
- **What it does:** a dedicated library for audiobooks and podcasts with listening progress that syncs across devices and mobile apps that download for offline listening.
- **Replaces:** audiobook subscriptions for books you own, plus separate podcast apps.
- **Where its data lives:** audiobooks, podcasts, app settings and generated metadata each get their own folder. Plan these before the first install.
- **Gotcha:** organize books as one folder per author and per title. Messy folders lead to messy libraries, and it's much easier to fix before you import than after.

### Samba: the shared drive
- **What it does:** turns a folder on the server into a network drive that appears on Windows, Mac, Linux and phones like any other disk.
- **Replaces:** passing around USB drives and paying for cloud storage for large files.
- **Where its data lives:** in the shared folders themselves. This is also the easiest place to drop new media for Jellyfin and Audiobookshelf to pick up.
- **Gotcha:** permissions. Create a proper user with a strong password instead of leaving shares open to everyone, and give each share only the access it needs. Keep Samba on your home network only and never expose it to the internet.

### How they fit together
Samba is the front door for files: copy movies, books and documents onto the server from any computer. Jellyfin and Audiobookshelf read from those folders, and Immich takes care of your phone's camera roll. Because they all share one folder layout on one storage drive, a single backup plan covers everything.

## Why a wrapper like CasaOS is the easiest approach

Underneath, almost every self-hosted app today runs as a container. Doing this by hand means installing a container engine, writing a configuration for every app, mapping folders and ports, and remembering what you did six months later. A wrapper turns that into a point-and-click experience.

- **App store instead of config files.** Installing an app is one click. The wrapper fills in sensible defaults for folders, ports and permissions.
- **One dashboard.** You can see what's running, start or stop things, and check resource use without opening a terminal.
- **Still real Linux underneath.** Nothing is locked away. The apps are ordinary containers, so you can open a terminal and tinker whenever you want.
- **Portable knowledge.** The skills you build (containers, folder layout, backups) carry over to any other tool or to doing it by hand later.
- **Lower risk of a messy setup.** Consistent folder structure and naming mean your future self can understand what past you did.

**Trade-offs to be honest about:** wrappers can lag behind the newest app versions, a project can slow down or change direction, and some advanced settings still need the terminal. Before committing, check that the project is actively maintained and that the apps you want are in its store. Similar projects exist, so pick the one that is healthiest at the time you read this.

## Setup method that works on any Linux flavor

Distributions and versions change. These steps don't.

### 1. Start with the hardware you have
An old laptop, a mini PC or a Raspberry Pi is plenty for a first server. Prioritize reliable storage and a wired network connection over raw speed. If you plan to transcode video, check that your chip supports hardware video decoding.

### 2. Choose a stable, boring operating system
Pick a long-term-support release from a mainstream distribution and install the minimal or server edition. Stability matters more than novelty on a machine you want to forget about. Check the wrapper's documentation for which distributions it officially supports and choose from that list.

### 3. Give the server a permanent address
Reserve a fixed address for the server in your router's settings, so the address of your apps never changes. This single step prevents most "it stopped working" moments.

### 4. Install the wrapper using its official instructions
Always follow the project's own current install guide rather than an old blog post (including this one). Read it fully before starting, because requirements change.

### 5. Plan your storage before installing apps
Decide where app settings live and where your big files live, and keep them separate. Ideally put your data on a separate drive from the operating system. This makes upgrades, rebuilds and backups far easier.

### 6. Install apps one at a time
After each install, open the app, confirm it works, and finish its first-run setup before adding the next. If something breaks, you know exactly which change caused it.

### 7. Handle access and security early
- Create strong, unique passwords and turn on two-factor authentication where offered.
- Keep the server off the open internet. For remote access, use a private VPN or a secure tunnelling service rather than forwarding ports on your router.
- Only expose what you actually need.

### 8. Set up backups before you need them
Follow the 3-2-1 idea: three copies of your data, on two kinds of storage, with one stored off-site. Back up app settings as well as your files. Then test a restore at least once, because an untested backup is only a hope.

### 9. Keep it updated on a schedule
Pick a regular day, for example once a month, to update the operating system, the wrapper and your apps. Read release notes before big updates, and take a backup first.

## Habits that save headaches later

- **Keep a plain-text notes file** listing every app, why you installed it, and any non-default choice you made.
- **Change one thing at a time** and test before moving on.
- **Don't expose or install what you don't use.** Fewer apps means fewer things to update and secure.
- **Check an app's maintenance status** before adopting it. Recent updates and an active community are good signs.
- **When something breaks, read the app's logs first.** They usually name the problem directly.

## Final thoughts

The goal of a home server is to own your data and enjoy useful tools without it becoming a second job. A wrapper handles the repetitive plumbing, and the method above keeps the setup understandable, backed up and easy to rebuild. Start with one or two apps, get comfortable, and grow from there.
