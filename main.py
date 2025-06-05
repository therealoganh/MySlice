from datetime import datetime
import json
from flask import Flask, make_response, render_template, request, redirect, url_for

app = Flask(__name__)

POSTS_FILE = 'posts.json'
now = datetime.now()


def load_posts():
    try:
        with open(POSTS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_posts(posts):
    with open(POSTS_FILE, 'w') as f:
        json.dump(posts, f, indent=4)


# Home route
@app.route('/')
def home():
    posts = load_posts()

    current_author = request.cookies.get('author')
    current_avatar = request.cookies.get('avatar')
    current_color = request.cookies.get('color')
    
    print("Loaded posts:", posts)
    
    return render_template('home.html',
                           posts=posts,
                           current_author=current_author,
                           current_avatar=current_avatar,
                           current_color=current_color
                          )


# Create post route
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form['author']
        avatar = request.form['avatar']
        color = request.form['color']
        timestamp = f"{now.month}/{now.day} {now.strftime('%I:%M %p')}"

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
        resp.set_cookie('author', author, max_age=60*60*24*365)
        resp.set_cookie('avatar', avatar, max_age=60*60*24*365)
        resp.set_cookie('color', color, max_age=60*60*24*365)

        return resp

    author = request.cookies.get('author', '')
    avatar = request.cookies.get('avatar', '')
    color = request.cookies.get('color', '#000000')

    return render_template('create.html', author=author, avatar=avatar, color=color)


# Delete post route (fix condition)
@app.route('/delete/<int:post_index>', methods=['POST'])
def delete(post_index):
    posts = load_posts()

    # Delete only if index is valid
    if 0 <= post_index < len(posts):
        deleted_post = posts.pop(post_index)  # Remove post at index
        print("Deleted:", deleted_post)
        save_posts(posts)

    return redirect(url_for('home'))


# Delete reply route (looks fine)
@app.route('/delete_reply/<int:post_index>/<int:reply_index>', methods=['POST'])
def delete_reply(post_index, reply_index):
    posts = load_posts()

    if 0 <= post_index < len(posts):
        post = posts[post_index]
        if 'replies' in post and 0 <= reply_index < len(post['replies']):
            current_author = request.cookies.get('author', '')
            reply_author = post['replies'][reply_index].get('author', '')

            if current_author == reply_author:
                deleted_reply = post['replies'].pop(reply_index)
                print('Deleted reply:', deleted_reply)
                save_posts(posts)
            else:
                print('Unauthorized delete reply attempt by', current_author)

    return redirect(url_for('home'))




@app.route('/edit/<int:post_index>', methods=['GET', 'POST'])
def edit(post_index):
    posts = load_posts()

    if 0 <= post_index < len(posts):
        return "Post not found", 404

    if request.method == 'POST':
        posts[post_index]['title'] = request.form['title']
        posts[post_index]['content'] = request.form['content']
        posts[post_index]['timestamp'] = (
            f"Edited {datetime.now().strftime('%m/%d %I:%M %p')}")
        save_posts(posts)
        return redirect(url_for('home'))

    post = posts[post_index]
    return render_template('edit.html', post=post, post_index=post_index)

# Reply route
@app.route('/reply/<int:post_index>', methods=['POST'])
def reply(post_index):
    posts = load_posts()

    if 0 <= post_index < len(posts):
        author = request.cookies.get('author', 'Anonymous')
        avatar = request.cookies.get('avatar', '👤')
        color = request.cookies.get('color', '#000000')
        content = request.form['content']
        timestamp = datetime.now().strftime('%m/%d %I:%M %p')

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

    
if __name__ == '__main__':
    app.run(debug=True)
