from colorama import *
from datetime import datetime, timezone
from fake_useragent import FakeUserAgent
from faker import Faker
from time import sleep
import gc
import json
import os
import pytz
import random
import requests
import sys


class Blum:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.faker = Faker()
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Host': 'game-domain.blum.codes',
            'Origin': 'https://telegram.blum.codes',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': FakeUserAgent().random
        }

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_timestamp(self, message):
        now = datetime.now(pytz.timezone('Asia/Jakarta'))
        timestamp = now.strftime(f'%x %X %Z')
        print(
            f"{Fore.BLUE + Style.BRIGHT}[ {timestamp} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{message}",
            flush=True
        )

    def auth(self):
        url = 'https://gateway.blum.codes/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP'
        try:
            if not os.path.exists('queries.txt'):
                with open('queries.txt', 'w') as f:
                    f.write('query_id=xxx')
                raise FileNotFoundError("File 'queries.txt' Not Found. The File Has Been Created. Please Fill It With Queries")

            with open('queries.txt', 'r') as f:
                queries = [line.strip() for line in f.readlines()]

            if not queries:
                raise ValueError("File 'queries.txt' Is Empty. Please Fill It With Queries")

            accounts = []
            for query in queries:
                if not query:
                    self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Empty Query Found, Skipping... ]{Style.RESET_ALL}")
                    continue

                data = json.dumps({'query': query})
                headers = {
                    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                    'Cache-Control': 'no-cache',
                    'Host': 'gateway.blum.codes',
                    'Pragma': 'no-cache',
                    'Origin': 'https://telegram.blum.codes',
                    'Pragma': 'no-cache',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-site',
                    'User-Agent': FakeUserAgent().random
                }
                response = self.session.post(url=url, headers=headers, data=data)
                response.raise_for_status()
                data = response.json()
                token = f"Bearer {data['token']['refresh']}"
                username = data['token'].get('user', {}).get('username', '').strip()
                if not username:
                    username = self.faker.user_name()
                accounts.append({
                    'username': username,
                    'token': token
                })

            if not os.path.exists('accounts.json'):
                with open('accounts.json', 'w') as outfile:
                    json.dump({'accounts': []}, outfile, indent=4)
                self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ File 'accounts.json' Not Found. The File Has Been Created ]{Style.RESET_ALL}")

            with open('accounts.json', 'w') as outfile:
                json.dump({'accounts': accounts}, outfile, indent=4)

            return accounts
        except (FileNotFoundError, ValueError, requests.RequestException, json.JSONDecodeError) as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
            return []

    def my_tribe(self, token: str):
        url = 'https://game-domain.blum.codes/api/v1/tribe/my'
        self.headers.update({'Authorization': token})
        try:
            response = self.session.get(url=url, headers=self.headers)
            response.raise_for_status()
            my_tribe = response.json()
            if my_tribe is not None:
                if my_tribe['id'] == 'ac4f8fcb-c68e-4ed8-afa9-a2ed3e7fab4c':
                    self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ You Are In {my_tribe['title']} Tribe ]{Style.RESET_ALL}")
                    self.print_timestamp(
                        f"{Fore.GREEN + Style.BRIGHT}[ Earn Balance 🍀 {int(float(my_tribe['earnBalance']))} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE + Style.BRIGHT}[ {my_tribe['countMembers']} Members 👩🏻‍🚀 In Tribe ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}[ Rank {my_tribe['rank']} 🏆 ]{Style.RESET_ALL}"
                    )
                else:
                    self.leave_tribe(token=token, tribe_title=my_tribe['title'])
            else:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Data In My Tribe Is None ]{Style.RESET_ALL}")
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                self.print_timestamp(
                    f"{Fore.RED + Style.BRIGHT}[ You Did Not Join In Any Tribe ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}[ Please Wait 3 Seconds To Joining Shyzago Tribe ]{Style.RESET_ALL}"
                )
                sleep(3)
                self.join_tribe(token=token)
            elif e.response.status_code == 500:
                try:
                    error_message = e.response.json()
                    if error_message['message'] == 'redis: connection pool timeout' or 'dial tcp 10.114.0.151:6379: i/o timeout':
                        self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Timeout Fetching My Tribe ]{Style.RESET_ALL}")
                    else:
                        self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Fetching My Tribe: {str(e)} ]{Style.RESET_ALL}")
                except ValueError:
                    self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Error: Unable To Parse Error Message In My Tribe ]{Style.RESET_ALL}")
            else:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Fetching My Tribe: {str(e)} ]{Style.RESET_ALL}")
        except requests.RequestException as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ A Request Error Occurred While Fetching My Tribe: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Fetching My Tribe: {str(e)} ]{Style.RESET_ALL}")

    def join_tribe(self, token: str):
        url = 'https://game-domain.blum.codes/api/v1/tribe/0999c4b7-1bbd-4825-a7a0-afc1bfb3fff6/join'
        self.headers.update({
            'Authorization': token,
            'Content-Length': '0'
        })
        try:
            response = self.session.post(url=url, headers=self.headers)
            response.raise_for_status()
            self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Thank You For Joining Shyzago Tribe ]{Style.RESET_ALL}")
        except requests.HTTPError as e:
            if e.response.status_code == 500:
                try:
                    error_message = e.response.json()
                    if error_message['message'] == 'redis: connection pool timeout' or 'dial tcp 10.114.0.151:6379: i/o timeout':
                        self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Timeout Joining Tribe ]{Style.RESET_ALL}")
                    else:
                        self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Joining The Tribe: {str(e)} ]{Style.RESET_ALL}")
                except ValueError:
                    self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Error: Unable To Parse Error Message In Join Tribe ]{Style.RESET_ALL}")
            else:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Joining The Tribe: {str(e)} ]{Style.RESET_ALL}")
        except requests.RequestException as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ A Request Error Occurred While Joining The Tribe: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Joining The Tribe: {str(e)} ]{Style.RESET_ALL}")

    def leave_tribe(self, token: str, tribe_title: str):
        url = 'https://game-domain.blum.codes/api/v1/tribe/leave'
        data = json.dumps({})
        self.headers.update({
            'Authorization': token,
            'Content-Length': str(len(data)),
            'Content-Type': 'application/json'
        })
        try:
            response = self.session.post(url=url, headers=self.headers, data=data)
            response.raise_for_status()
            self.print_timestamp(
                f"{Fore.RED + Style.BRIGHT}[ Leaving {tribe_title} Tribe. ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}[ Please Wait 3 Seconds To Join {tribe_title} Tribe ]{Style.RESET_ALL}"
            )
            sleep(3)
            self.join_tribe(token=token)
        except requests.HTTPError as e:
            if e.response.status_code == 500:
                try:
                    error_message = e.response.json()
                    if error_message['message'] == 'redis: connection pool timeout' or 'dial tcp 10.114.0.151:6379: i/o timeout':
                        self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Timeout ]{Style.RESET_ALL}")
                    elif error_message['message'] == 'user is not in a tribe':
                        self.print_timestamp(
                            f"{Fore.YELLOW + Style.BRIGHT}[ You Are Not In A Tribe ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT}[ Please Wait 3 Seconds To Join {tribe_title} Tribe ]{Style.RESET_ALL}"
                        )
                        sleep(3)
                        self.join_tribe(token=token)
                    else:
                        self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Leaving The Tribe: {str(e)} ]{Style.RESET_ALL}")
                except ValueError:
                    self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Error: Unable To Parse Error Message In Leave Tribe ]{Style.RESET_ALL}")
            else:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Leaving The Tribe: {str(e)} ]{Style.RESET_ALL}")
        except requests.RequestException as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ A Request Error Occurred While Leaving The Tribe: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Leaving The Tribe: {str(e)} ]{Style.RESET_ALL}")

    def daily_reward(self, token: str):
        url = 'https://game-domain.blum.codes/api/v1/daily-reward?offset=-420'
        self.headers.update({
            'Authorization': token,
            'Content-Length': '0'
        })
        try:
            response = requests.post(url=url, headers=self.headers)
            response.raise_for_status()
            self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Claimed Daily Reward ]{Style.RESET_ALL}")
        except requests.HTTPError as e:
            if e.response.status_code == 400:
                self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Daily Reward Already Claimed ]{Style.RESET_ALL}")
            else:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Claiming Daily Reward: {str(e)} ]{Style.RESET_ALL}")
        except requests.RequestException as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ A Request Error Occurred While Claiming Daily Reward: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Claiming Daily Reward: {str(e)} ]{Style.RESET_ALL}")

    def user_balance(self, token: str):
        url = 'https://game-domain.blum.codes/api/v1/user/balance'
        self.headers.update({'Authorization': token})
        try:
            response = requests.get(url=url, headers=self.headers)
            response.raise_for_status()
            user_balance = response.json()
            if user_balance is not None:
                return user_balance
            else:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Data In User Balance Is None ]{Style.RESET_ALL}")
        except requests.HTTPError as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Fetching User Balance: {str(e)} ]{Style.RESET_ALL}")
        except requests.RequestException as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ A Error Occurred While Fetching User Balance: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Fetching User Balance: {str(e)} ]{Style.RESET_ALL}")

    def start_farming(self, token: str):
        url = 'https://game-domain.blum.codes/api/v1/farming/start'
        self.headers.update({
            'Authorization': token,
            'Content-Length': '0'
        })
        try:
            response = requests.post(url=url, headers=self.headers)
            response.raise_for_status()
            start_farming = response.json()
            if start_farming is not None:
                self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Farming Started ]{Style.RESET_ALL}")
                end_time = datetime.fromtimestamp(start_farming['endTime'] / 1000, tz=timezone.utc)
                now_utc = datetime.now(timezone.utc)
                end_time_wib = end_time.astimezone(pytz.timezone('Asia/Jakarta'))
                formatted_end_time = end_time_wib.strftime('%x %X %Z')
                if now_utc > end_time:
                    self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Claiming Farming ]{Style.RESET_ALL}")
                    self.claim_farming(token=token)
                else:
                    self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Farming Can Claim At {formatted_end_time} ]{Style.RESET_ALL}")
            else:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Data In Start Farming Is None ]{Style.RESET_ALL}")
        except requests.HTTPError as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Starting Farming: {str(e)} ]{Style.RESET_ALL}")
        except requests.RequestException as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ A Request Error Occurred While Starting Farming: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Starting Farming: {str(e)} ]{Style.RESET_ALL}")

    def claim_farming(self, token: str, available_balance: str):
        url = 'https://game-domain.blum.codes/api/v1/farming/claim'
        self.headers.update({
            'Authorization': token,
            'Content-Length': '0'
        })
        try:
            response = requests.post(url=url, headers=self.headers)
            response.raise_for_status()
            claim_farming = response.json()
            if claim_farming is not None:
                self.print_timestamp(
                    f"{Fore.GREEN + Style.BRIGHT}[ Farming Claimed 🍀 {int(float(claim_farming['availableBalance'])) - int(float(available_balance))} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT}[ Updated Balance 🍀 {int(float(claim_farming['availableBalance']))} ]{Style.RESET_ALL}"
                )
                self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Starting Farming ]{Style.RESET_ALL}")
                self.start_farming(token=token)
            else:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Data In Claim Farming Is None ]{Style.RESET_ALL}")
        except requests.HTTPError as e:
            if e.response.status_code == 412:
                self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Need To Start Farming. Starting Now ]{Style.RESET_ALL}")
                self.start_farming(token=token)
            elif e.response.status_code == 425:
                self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ It's Too Early To Claim ]{Style.RESET_ALL}")
            else:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Claiming Farming: {str(e)} ]{Style.RESET_ALL}")
        except requests.RequestException as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ A Request Error Occurred While Claiming Farming: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Claiming Farming: {str(e)} ]{Style.RESET_ALL}")

    def game_play(self, token: str):
        url = 'https://game-domain.blum.codes/api/v1/game/play'
        self.headers.update({
            'Authorization': token,
            'Content-Length': '0'
        })
        try:
            response = requests.post(url=url, headers=self.headers)
            response.raise_for_status()
            game_play = response.json()
            if game_play is not None:
                if 'gameId' in game_play:
                    if game_play['gameId'] is not None:
                        sleep(33)
                        self.game_claim(token=token, game_id=game_play['gameId'], points=random.randint(1000, 1001))
                    else:
                        self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ 'gameId' In Game Play Is None ]{Style.RESET_ALL}")
                else:
                    self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ There Is No 'gameId' In Game Play ]{Style.RESET_ALL}")
            else:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Data In Game Play Is None ]{Style.RESET_ALL}")
        except requests.HTTPError as e:
            if e.response.status_code == 400:
                self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Not Enough Play Passes ]{Style.RESET_ALL}")
            else:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Playing The Game: {str(e)} ]{Style.RESET_ALL}")
        except requests.RequestException as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ A Request Error Occurred While Playing The Game: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Playing The Game: {str(e)} ]{Style.RESET_ALL}")

    def game_claim(self, token: str, game_id: str, points: int):
        url = 'https://game-domain.blum.codes/api/v1/game/claim'
        data = json.dumps({'gameId': game_id, 'points': points})
        self.headers.update({
            'Authorization': token,
            'Content-Length': str(len(data)),
            'Content-Type': 'application/json'
        })
        try:
            response = requests.post(url=url, headers=self.headers, data=data)
            response.raise_for_status()
            self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Game Claimed ]{Style.RESET_ALL}")
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Game Session Not Found ]{Style.RESET_ALL}")
            else:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Claiming The Game: {str(e)} ]{Style.RESET_ALL}")
        except requests.RequestException as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ A Request Error Occurred While Claiming The Game: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Claiming The Game: {str(e)} ]{Style.RESET_ALL}")

    def tasks(self, token: str):
        url = 'https://game-domain.blum.codes/api/v1/tasks'
        self.headers.update({'Authorization': token})
        try:
            response = requests.get(url=url, headers=self.headers)
            response.raise_for_status()
            tasks = response.json()
            for category in tasks:
                for task in category['tasks']:
                    if task['type'] in ["WALLET_CONNECTION", "APPLICATION_LAUNCH"] or "Subscribe" in task['title'] or "Telegram" in task['title']:
                        continue
                    if 'socialSubscription' in task:
                        if task['status'] == 'NOT_STARTED':
                            self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Starting {task['title']} ]{Style.RESET_ALL}")
                            self.tasks_start(token=token, task_id=task['id'], task_title=task['title'])
                        elif task['status'] == 'READY_FOR_CLAIM':
                            self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Claiming {task['title']} ]{Style.RESET_ALL}")
                            self.tasks_claim(token=token, task_id=task['id'], task_title=task['title'])
                    elif 'progressTarget' in task:
                        if (float(task['progressTarget']['progress']) >= float(task['progressTarget']['target']) and
                            task['status'] == 'READY_FOR_CLAIM'):
                            self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Claiming {task['title']} ]{Style.RESET_ALL}")
                            self.tasks_claim(token=token, task_id=task['id'], task_title=task['title'])
        except requests.HTTPError as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Fetching Tasks: {str(e)} ]{Style.RESET_ALL}")
        except requests.RequestException as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ A Request Error Occurred While Fetching Tasks: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Fetching Tasks: {str(e)} ]{Style.RESET_ALL}")

    def tasks_start(self, token: str, task_id: str, task_title: str):
        url = f'https://game-domain.blum.codes/api/v1/tasks/{task_id}/start'
        self.headers.update({'Authorization': token})
        try:
            response = requests.post(url=url, headers=self.headers)
            response.raise_for_status()
            self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ {task_title} Started. Please Wait 3 Second To Claiming Task ]{Style.RESET_ALL}")
            sleep(3)
            self.tasks_claim(token=token, task_id=task_id, task_title=task_title)
        except requests.HTTPError as e:
            if e.response.status_code == 400:
                self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ {task_title} Already Started Or Claimed ]{Style.RESET_ALL}")
            elif e.response.status_code == 500:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Cannot Get Tasks ]{Style.RESET_ALL}")
            else:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Fetching Tasks: {str(e)} ]{Style.RESET_ALL}")
        except requests.RequestException as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ A Request Error Occurred While Fetching Tasks: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Starting The Task: {str(e)} ]{Style.RESET_ALL}")

    def tasks_claim(self, token: str, task_id: str, task_title: str):
        url = f'https://game-domain.blum.codes/api/v1/tasks/{task_id}/claim'
        self.headers.update({'Authorization': token})
        try:
            response = requests.post(url=url, headers=self.headers)
            response.raise_for_status()
            self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Claimed {task_title} ]{Style.RESET_ALL}")
        except requests.HTTPError as e:
            if e.response.status_code == 400:
                self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ {task_title} Already Claimed ]{Style.RESET_ALL}")
            elif e.response.status_code == 412:
                self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ {task_title} Not Done. Please Wait 3 Seconds To Start Again ]{Style.RESET_ALL}")
                sleep(3)
                self.tasks_start(token=token, task_id=task_id, task_title=task_title)
            elif e.response.status_code == 500:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Cannot Get Tasks ]{Style.RESET_ALL}")
            else:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Claiming The Task: {str(e)} ]{Style.RESET_ALL}")
        except requests.RequestException as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ A Request Error Occurred While Claiming The Task: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Claiming The Task: {str(e)} ]{Style.RESET_ALL}")

    def main(self):
        while True:
            try:
                accounts = self.auth()
                if not accounts:
                    self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ No Accounts To process. Exiting ]{Style.RESET_ALL}")
                    return
                self.print_timestamp(f"{Fore.WHITE + Style.BRIGHT}[ ————— Information ————— ]{Style.RESET_ALL}")
                for account in accounts:
                    self.print_timestamp(f"{Fore.CYAN + Style.BRIGHT}[ {account['username']} ]{Style.RESET_ALL}")
                    self.daily_reward(token=account['token'])
                    user_balance = self.user_balance(token=account['token'])
                    self.print_timestamp(
                        f"{Fore.GREEN + Style.BRIGHT}[ 🍀 Balance {int(float(user_balance['availableBalance']))} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE + Style.BRIGHT}[ 🎫 Play Passes {user_balance['playPasses']} ]{Style.RESET_ALL}"
                    )
                    if 'farming' in user_balance:
                        end_time = datetime.fromtimestamp(user_balance['farming']['endTime'] / 1000, tz=timezone.utc)
                        now_utc = datetime.now(timezone.utc)
                        end_time_wib = end_time.astimezone(pytz.timezone('Asia/Jakarta'))
                        formatted_end_time = end_time_wib.strftime('%x %X %Z')
                        if now_utc > end_time:
                            self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Claiming Farming ]{Style.RESET_ALL}")
                            self.claim_farming(token=account['token'], available_balance=user_balance['availableBalance'])
                        else:
                            self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Farming Can Claim At {formatted_end_time} ]{Style.RESET_ALL}")
                    else:
                        self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Starting Farming ]{Style.RESET_ALL}")
                        self.start_farming(token=account['token'])
                    self.my_tribe(token=account['token'])
                self.print_timestamp(f"{Fore.WHITE + Style.BRIGHT}[ ————— Tasks ————— ]{Style.RESET_ALL}")
                for account in accounts:
                    self.print_timestamp(f"{Fore.CYAN + Style.BRIGHT}[ {account['username']} ]{Style.RESET_ALL}")
                    self.tasks(token=account['token'])
                self.print_timestamp(f"{Fore.WHITE + Style.BRIGHT}[ ————— Play Passes ————— ]{Style.RESET_ALL}")
                for account in accounts:
                    play_passes = self.user_balance(token=account['token'])
                    if play_passes['playPasses'] != 0:
                        while play_passes['playPasses'] > 0:
                            self.print_timestamp(
                                f"{Fore.GREEN + Style.BRIGHT}[ Game Started ]{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                                f"{Fore.BLUE + Style.BRIGHT}[ Please Wait 30 Seconds ]{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT}[ {account['username']} ]{Style.RESET_ALL}"
                            )
                            self.game_play(token=account['token'])
                            play_passes['playPasses'] -= 1
                    else:
                        self.print_timestamp(
                            f"{Fore.YELLOW + Style.BRIGHT}[ Not Enough Play Passes ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}[ {account['username']} ]{Style.RESET_ALL}"
                        )
                self.print_timestamp(f"{Fore.CYAN + Style.BRIGHT}[ Restarting Soon ]{Style.RESET_ALL}")
                sleep(3600)
                self.clear_terminal()
                gc.collect()
            except Exception as e:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")


if __name__ == '__main__':
    while True:
        try:
            init(autoreset=True)
            blum = Blum()
            blum.main()
        except (Exception, requests.ConnectionError, requests.JSONDecodeError) as e:
            blum.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
        except KeyboardInterrupt:
            blum.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ See You 👋🏻 ]{Style.RESET_ALL}")
            sys.exit(0)