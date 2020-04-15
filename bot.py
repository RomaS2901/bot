import json
import os
import random
import time
import string

import requests

API_URL = "http://127.0.0.1:8000"
CONFIG_FILENAME = "init.json"
CONFIG_PATH = os.path.join(os.path.dirname(__file__), CONFIG_FILENAME)


def generate_random_password():
    # first letter always upper, next random 10 ascii letter and hash of unix time sec
    return f'{random.choice(string.ascii_uppercase)}{"".join(random.choices(string.ascii_letters, k=10))}{hash(int(time.time()))}'


def read_config(config_path: str) -> tuple:
    with open(config_path) as file:
        config = json.loads(file.read())
    return (
        config["numberOfUsers"],
        config["maxPostPerUser"],
        config["maxLikesPerUser"],
    )


def signup_and_login(username: str = None, password: str = None) -> tuple:
    """ Register new user. Logs in, returns token to use in next requests """
    user_data = {
        "username": username or f"bot_{int(time.time())}",
        "password": password or generate_random_password(),
    }
    sign_up_response = requests.post(f"{API_URL}/accounts/signup/", data=user_data)
    sign_up_response.raise_for_status()
    username = sign_up_response.json()[
        "username"
    ]  # to vertify that server sent back new username
    login_response = requests.post(f"{API_URL}/accounts/token/", data=user_data)
    login_response.raise_for_status()
    print(f'Successfully created and loged in user: "{username}"...')
    return username, login_response.json()["access"]


def create_posts(
    posts_num: int, username: str, token, title: str = None, body: str = None
):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    for n in range(posts_num):
        post = {
            "title": title or f"Post {int(time.time())}",
            "body": body or f"Post body :) Here was a bot!",
            "user": username,
        }
        response = requests.post(f"{API_URL}/posts/", json=post, headers=headers)
        response.raise_for_status()
        post = response.json()
        print(
            f'{n+1}: post created! Title: "{post["title"]}", body: "{post["body"]}" for "{username}"...',
        )


def like_posts(likes_num, token):
    # get all id's of presented posts and generate choices iterable with id's os posts to like
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    posts_response = requests.get(f"{API_URL}/posts/", headers=headers)
    posts_response.raise_for_status()
    post_id_choices = [post["id"] for post in posts_response.json()]

    for n in range(likes_num):
        post_id = random.choice(post_id_choices)
        response = requests.post(f"{API_URL}/posts/{post_id}/like/", headers=headers)
        response.raise_for_status()
        liked_post = response.json()
        print(
            f'{n+1}: liked post with title: "{liked_post["title"]}" by "{liked_post["user"]}"...',
        )


def main():
    users_n, posts_n, likes_n = read_config(CONFIG_PATH)
    for n in range(users_n):
        username, token = signup_and_login()
        create_posts(posts_n, username, token)
        like_posts(likes_n, token)
    print("=" * 20)
    print(
        f"Bot finished\n{users_n}: users created, {posts_n}: posts created, {likes_n} likes left :) ",
    )
    print("=" * 20)


if __name__ == "__main__":
    main()
