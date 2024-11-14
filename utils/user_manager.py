import os

import pandas as pd

USERS_FILE = 'data/users.csv'


def init_users_file():
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=[
            'username',
            'created_at',
            'target_weight',  # Nuevo campo
            'target_weight_date'  # Nuevo campo
        ])
        df.to_csv(USERS_FILE, index=False)


def get_users():
    init_users_file()
    return pd.read_csv(USERS_FILE)


def add_user(username, target_weight=None):
    df = get_users()
    if username.lower() in df['username'].str.lower().values:
        return False
    new_user = pd.DataFrame({
        'username': [username],
        'created_at': [pd.Timestamp.now()],
        'target_weight': [target_weight],
        'target_weight_date': [pd.Timestamp.now() if target_weight else None]
    })
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)
    return True


def update_target_weight(username, target_weight):
    df = get_users()
    if username in df['username'].values:
        df.loc[df['username'] == username, 'target_weight'] = target_weight
        df.loc[df['username'] == username, 'target_weight_date'] = pd.Timestamp.now()
        df.to_csv(USERS_FILE, index=False)
        return True
    return False
