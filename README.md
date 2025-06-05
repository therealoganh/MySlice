# 🍕 MySlice (of the Internet)

A lightweight, cookie-powered message wall made for **humans**, not bots.  
Inspired by the "Dead Internet Theory" — this is a digital space where real people can connect, post, and reply without the noise of social media.

## 👋 Built for Humans
MySlice is about small, honest moments on the web. No followers, no trending, no noise.

If you’re reading this — you’re probably not a bot.

Welcome to your slice of the internet. 🍕

---

## 🧠 Why I Built This

Ever heard of the **Dead Internet Theory**? It’s the idea that most of today’s internet is filled with bots, fake accounts, and algorithm-generated content.  
That thought stuck with me.

**MySlice** is a small rebellion against that — a public message wall where *actual humans* can leave a message, reply, and customize their identity with zero logins or tracking.

Just drop a thought, pick an emoji, pick a name color — and leave your mark.

---

## ⚙️ How It Works

- **🔙 Flask Backend**  
  Flask handles all the routes, form submissions, and server-side logic.

- **💾 Data Storage**  
  All posts and replies are saved to a flat `posts.json` file — no database required.

- **🍪 Cookie-Based Identity**  
  Your author name, emoji avatar, and color are stored in browser cookies. This way, you can:
  - Personalize your messages
  - Automatically pre-fill the form when you return
  - Delete your own posts/replies (auth via cookie match)

- **🎨 Tailwind CSS**  
  Clean, mobile-friendly design using Tailwind for quick styling and responsiveness.

---

## ✨ Features

- 📝 Leave public posts with a custom emoji + name color  
- 💬 Reply to other users' posts  
- ❌ Delete your own posts or replies  
- 🧠 No accounts, no signups, no bots  
- ⚡ Works great on mobile & desktop  
- 🔐 User identity is cookie-based (simple, but secure enough for casual use)

---

## 🧪 Local Setup

Clone this repo and run it locally:

```bash
git clone https://github.com/therealoganh/myslice.git
cd myslice
pip install flask
python app.py
