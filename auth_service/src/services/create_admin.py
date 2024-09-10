import asyncio
import os
import sys
from getpass import getpass

import click

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../..')

from src.db.postgres import async_session
from src.schemas.user import UserCreate
from src.services.user import create_user_service


@click.command()
@click.option('--username', default='admin', help='Username for the new admin user.')
def create_admin_user(username: str):
    asyncio.run(run_create_admin_user(username))


async def run_create_admin_user(username: str):
    password = getpass('Enter password for admin: ')
    password_confirm = getpass('Confirm password: ')

    if password != password_confirm:
        click.echo("Passwords do not match!")
        return

    async with async_session() as db:
        user_data = UserCreate(
            login=username,
            password=password,
            first_name='',
            last_name='',
        )

        try:
            new_user = await create_user_service(user_data, db, role='admin')
            click.echo(f"Admin user '{new_user.login}' successfully created with role 'admin'.")
        except Exception as e:
            click.echo(f"Failed to create admin user: {e}\n")


if __name__ == '__main__':
    create_admin_user()
