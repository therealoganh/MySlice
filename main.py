from datetime import datetime, date
import json
from flask import Flask, make_response, render_template, request, redirect, url_for
import pytz
from replit import db

app = Flask(__name__)

POSTS_FILE = 'posts.json'

# Daily prompt feature
DAILY_PROMPTS = [
    "How do you think the latest advances in AI will change your day-to-day life?",
    "What’s your take on the recent climate initiatives—hopeful or skeptical?",
    "If you could ask a world leader one question about global peace, what would it be?",
    "What’s one technology you’re excited or concerned about becoming mainstream soon?",
    "How have recent social movements inspired or challenged your personal beliefs?",
    "What’s something you learned this week that surprised you?",
    "If you had to create a headline for your life today, what would it say?",
    "How do you stay hopeful when news seems overwhelming?",
    "What’s a change you want to see in your community this year?",
    "If you could share one piece of advice about adapting to change, what would it be?"
]


def get_daily_prompt():
    central = pytz.timezone('America/Chicago')
    today = datetime.now(central).date()
    day_index = today.toordinal() % len(DAILY_PROMPTS)
    return DAILY_PROMPTS[day_index]
    

# Poll Functionality
POLL_FILE = 'poll.json'

DEFAULT_POLL = {
    "Dark Mode": 0,
    "Emojis": 0,
    "Themes": 0,
    "More Prompts": 0
}

def load_poll():
    return db.get("poll", DEFAULT_POLL.copy())

def save_poll(poll):
    db['poll'] = poll

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    poll = load_poll()
    has_voted = request.cookies.get('voted')

    if request.method == 'POST' and not has_voted:
        choice = request.form.get('feature')
        if choice in poll:
            poll[choice] += 1
            save_poll(poll)
            resp = make_response(redirect(url_for('vote')))
            resp.set_cookie('voted', 'yes', max_age=60*60*24*365)
            return resp

    return render_template('vote.html', poll=poll,has_voted=has_voted)

# Easter egg functionality
@app.route('/slice')
def slice_secret():
    return render_template('slice.html')

# Utility Functions
def load_posts():
    return db.get("posts", [])


def save_posts(posts):
    db['posts'] = posts

# MAIN ROUTES


# Default Home Route
@app.route('/')
def home():
    posts = load_posts()

    current_author = request.cookies.get('author')
    current_avatar = request.cookies.get('avatar')
    current_color = request.cookies.get('color')

    return render_template('home.html',
                           posts=posts,
                           current_author=current_author,
                           current_avatar=current_avatar,
                           current_color=current_color,
                          daily_prompt=get_daily_prompt())


# Create post route
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form['author']
        avatar = request.form['avatar']
        color = request.form['color']
        central = pytz.timezone('America/Chicago')
        timestamp = datetime.now(central).strftime('%m/%d %I:%M %p')

        posts = load_posts()
        posts.append({
            'title': title,
            'content': content.strip(),
            'author': author,
            'avatar': avatar,
            'color': color,
            'timestamp': timestamp
        })
        save_posts(posts)

        # Create response and set cookies
        resp = make_response(redirect(url_for('home')))
        resp.set_cookie('author', author, max_age=60 * 60 * 24 * 365)
        resp.set_cookie('avatar', avatar, max_age=60 * 60 * 24 * 365)
        resp.set_cookie('color', color, max_age=60 * 60 * 24 * 365)

        return resp

    author = request.cookies.get('author', '')
    avatar = request.cookies.get('avatar', '')
    color = request.cookies.get('color', '#000000')

    return render_template('create.html',
                           author=author,
                           avatar=avatar,
                           color=color)


# Edit post route
@app.route('/edit/<int:post_index>', methods=['GET', 'POST'])
def edit(post_index):
    posts = load_posts()
    central = pytz.timezone('America/Chicago')

    if not (0 <= post_index < len(posts)):
        return "Post not found", 404

    if request.method == 'POST':
        posts[post_index]['title'] = request.form['title']
        posts[post_index]['content'] = request.form['content']
        posts[post_index]['timestamp'] = (
            f"Edited {datetime.now(central).strftime('%m/%d %I:%M %p')}")
        save_posts(posts)
        return redirect(url_for('home'))

    post = posts[post_index]
    return render_template('edit.html', post=post, post_index=post_index)


# Reply to post route
@app.route('/reply/<int:post_index>', methods=['POST'])
def reply(post_index):
    posts = load_posts()
    central = pytz.timezone('America/Chicago')

    if 0 <= post_index < len(posts):
        author = request.cookies.get('author', 'Anonymous')
        avatar = request.cookies.get('avatar', '👤')
        color = request.cookies.get('color', '#000000')
        content = request.form['content']
        timestamp = datetime.now(central).strftime('%m/%d %I:%M %p')

        reply_data = {
            'author': author,
            'avatar': avatar,
            'color': color,
            'content': content,
            'timestamp': timestamp
        }

        # Append reply to the post's replies list
        if 'replies' not in posts[post_index]:
            posts[post_index]['replies'] = []
        posts[post_index]['replies'].append(reply_data)

        save_posts(posts)

    # Redirect back to home
    return redirect(url_for('home'))


# DELETE ROUTES
# Delete post route
@app.route('/delete/<int:post_index>', methods=['POST'])
def delete(post_index):
    posts = load_posts()
    current_author = request.cookies.get('author', '')
    logan_key = request.cookies.get('logan_key')
    is_logan = current_author == 'Logan' and logan_key == 'supersecretvalue'

    # Delete only if index is valid
    if 0 <= post_index < len(posts):
        post = posts[post_index]
        # Delete only if current author matches post author
        if current_author == post.get('author') or is_logan:
            posts.pop(post_index)  # Remove post at index
            save_posts(posts)

    return redirect(url_for('home'))


# Delete reply route
@app.route('/delete_reply/<int:post_index>/<int:reply_index>',
           methods=['POST'])

def delete_reply(post_index, reply_index):
    posts = load_posts()
    

    if 0 <= post_index < len(posts):
        post = posts[post_index]
        if 'replies' in post and 0 <= reply_index < len(post['replies']):
            current_author = request.cookies.get('author', '')
            reply_author = post['replies'][reply_index].get('author', '')
            is_logan = current_author == 'Logan' and request.cookies.get('logan_key') == 'supersecretvalue'

            # Only deletes reply if author matches
            if current_author == reply_author or current_author == is_logan:
                post['replies'].pop(reply_index)
                save_posts(posts)

    return redirect(url_for('home'))

# Special route
@app.route('/iamlogan')
def iamlogan():
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('logan_key', 'supersecretvalue', max_age=60 * 60 * 24 * 365)
    resp.set_cookie('author', 'Logan', max_age=60 * 60 * 24 * 365)
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
