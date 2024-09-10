from colorama import *
from datetime import datetime, timedelta
from fake_useragent import FakeUserAgent
from faker import Faker
import aiohttp
import asyncio
import json
import os
import random
import re
import sys

class Blum:
    def __init__(self) -> None:
        self.faker = Faker()
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
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
        print(
            f"{Fore.BLUE + Style.BRIGHT}[ {datetime.now().astimezone().strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{message}",
            flush=True
        )

    def process_queries(self, lines_per_file=25):
        if not os.path.exists('queries.txt'):
            raise FileNotFoundError(f"File 'queries.txt' not found. Please ensure it exists.")

        with open('queries.txt', 'r') as f:
            queries = [line.strip() for line in f if line.strip()]

        if not queries:
            raise ValueError("File 'queries.txt' is empty.")

        existing_queries = set()

        for file in os.listdir():
            if file.startswith('queries-') and file.endswith('.txt'):
                with open(file, 'r') as qf:
                    existing_queries.update(line.strip() for line in qf if line.strip())

        new_queries = [query for query in queries if query not in existing_queries]

        if not new_queries:
            self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ No New Queries To Add ]{Style.RESET_ALL}")
            return

        files = [f for f in os.listdir() if f.startswith('queries-') and f.endswith('.txt')]
        files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0)

        last_file_number = int(re.findall(r'\d+', files[-1])[0]) if files else 0

        for i in range(0, len(new_queries), lines_per_file):
            chunk = new_queries[i:i + lines_per_file]
            if files and len(open(files[-1], 'r').readlines()) < lines_per_file:
                with open(files[-1], 'a') as outfile:
                    outfile.write('\n'.join(chunk) + '\n')
                self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Updated '{files[-1]}' ]{Style.RESET_ALL}")
            else:
                last_file_number += 1
                queries_file = f"queries-{last_file_number}.txt"
                with open(queries_file, 'w') as outfile:
                    outfile.write('\n'.join(chunk) + '\n')
                self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Generated '{queries_file}' ]{Style.RESET_ALL}")

    def load_queries(self, file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]

    async def auth(self, queries):
        url = 'https://user-domain.blum.codes/api/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP'
        accounts = []
        for query in queries:
            if not query:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Empty Query Found ]{Style.RESET_ALL}")
                return
            data = json.dumps({'query':query,'referralToken':'ZaPCLmyAt5'})
            headers = {
                **self.headers,
                'Content-Length': str(len(data)),
                'Content-Type': 'application/json'
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        data = await response.json()
                        token = f"Bearer {data['token']['refresh']}"
                        username = data['token']['user']['username'] or self.faker.user_name()
                        accounts.append({'username': username, 'token': token})
            except (aiohttp.ClientResponseError, aiohttp.ContentTypeError, Exception) as e:
                self.print_timestamp(
                    f"{Fore.YELLOW + Style.BRIGHT}[ Failed To Process {query} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}"
                )
                continue
        return accounts

    async def daily_reward(self, token: str, username: str):
        url = 'https://game-domain.blum.codes/api/v1/daily-reward?offset=-420'
        data = json.dumps({})
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Length': str(len(data))
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    if response.status == 400:
                        return self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Daily Reward Already Claimed ]{Style.RESET_ALL}"
                        )

                    response.raise_for_status()
                    return self.print_timestamp(
                        f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT}[ Claimed Daily Reward ]{Style.RESET_ALL}"
                    )
        except (aiohttp.ClientResponseError, aiohttp.ContentTypeError) as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ A Request Error Occurred While Claiming Daily Reward: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Claiming Daily Reward: {str(e)} ]{Style.RESET_ALL}")

    async def user_balance(self, token: str):
        url = 'https://game-domain.blum.codes/api/v1/user/balance'
        headers = {
            **self.headers,
            'Authorization': token
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
        except (aiohttp.ClientResponseError, aiohttp.ContentTypeError) as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ A Error Occurred While Fetching User Balance: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Fetching User Balance: {str(e)} ]{Style.RESET_ALL}")

    async def start_farming(self, token: str, available_balance: str, username: str):
        url = 'https://game-domain.blum.codes/api/v1/farming/start'
        data = json.dumps({})
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Length': str(len(data))
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    start_farming = await response.json()

                    self.print_timestamp(
                        f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT}[ Farming Started ]{Style.RESET_ALL}"
                    )

                    if datetime.now().astimezone() >= datetime.fromtimestamp(start_farming['endTime'] / 1000).astimezone():
                        return await self.claim_farming(token=token, available_balance=available_balance, username=username)

                    formatted_end_time = datetime.fromtimestamp(start_farming['endTime'] / 1000).astimezone().strftime('%x %X %Z')
                    return self.print_timestamp(
                        f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}[ Farming Can Be Claimed At {formatted_end_time} ]{Style.RESET_ALL}"
                    )
        except (aiohttp.ClientResponseError, aiohttp.ContentTypeError) as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Starting The Farming: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Starting The Farming: {str(e)} ]{Style.RESET_ALL}")

    async def claim_farming(self, token: str, available_balance: str, username: str):
        url = 'https://game-domain.blum.codes/api/v1/farming/claim'
        data = json.dumps({})
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Length': str(len(data))
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    if response.status == 412:
                        self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ Need To Start Farming ]{Style.RESET_ALL}"
                        )
                        return await self.start_farming(token=token, available_balance=available_balance, username=username)
                    elif response.status == 425:
                        return self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ It's Too Early To Claim The Farming ]{Style.RESET_ALL}"
                        )
                    elif response.status == 520:
                        return self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ Server Blum Error ]{Style.RESET_ALL}"
                        )
                    else:
                        response.raise_for_status()
                        claim_farming = await response.json()
                        self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}[ Farming Claimed {int(float(claim_farming['availableBalance'])) - int(float(available_balance))} ]{Style.RESET_ALL}"
                        )
                        return await self.start_farming(token=token, available_balance=available_balance, username=username)
        except (aiohttp.ClientResponseError, aiohttp.ContentTypeError) as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Claiming The Farming: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Claiming The Farming: {str(e)} ]{Style.RESET_ALL}")

    async def play_game(self, token: str, username: str):
        url = 'https://game-domain.blum.codes/api/v1/game/play'
        data = json.dumps({})
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Length': str(len(data))
        }
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        if response.status == 400:
                            self.print_timestamp(
                                f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT}[ Not Enough Play Passes ]{Style.RESET_ALL}"
                            )
                            break
                        response.raise_for_status()
                        game_play = await response.json()
                        self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}[ Game Started ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT}[ Please Wait 30 Seconds ]{Style.RESET_ALL}"
                        )
                        await asyncio.sleep(30 + random.randint(3, 5))
                        await self.claim_game(token=token, game_id=game_play['gameId'], points=random.randint(1000, 1001), username=username)
            except (aiohttp.ClientResponseError, aiohttp.ContentTypeError) as e:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Playing The Game: {str(e)} ]{Style.RESET_ALL}")
                break
            except Exception as e:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Playing The Game: {str(e)} ]{Style.RESET_ALL}")
                break

    async def claim_game(self, token: str, game_id: str, points: int, username: str):
        url = 'https://game-domain.blum.codes/api/v1/game/claim'
        data = json.dumps({'gameId':game_id,'points':points})
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Length': str(len(data)),
            'Content-Type': 'application/json'
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    if response.status == 404:
                        return self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ Game Session Not Found ]{Style.RESET_ALL}"
                        )
                    response.raise_for_status()
                    return self.print_timestamp(
                        f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT}[ Game Claimed ]{Style.RESET_ALL}"
                    )
        except (aiohttp.ClientResponseError, aiohttp.ContentTypeError) as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Claiming The Game: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Claiming The Game: {str(e)} ]{Style.RESET_ALL}")

    async def tasks(self, token: str, username: str):
        url = 'https://game-domain.blum.codes/api/v1/tasks'
        headers = {
            **self.headers,
            'Authorization': token
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url, headers=headers) as response:
                    if response.status == 500:
                        return self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ Cannot Get Tasks ]{Style.RESET_ALL}"
                        )
                    elif response.status == 520:
                        return self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ Server Blum Error ]{Style.RESET_ALL}"
                        )
                    else:
                        response.raise_for_status()
                        tasks = await response.json()
                        for category in tasks:
                            for section in category['subSections']:
                                for task in section['tasks']:
                                    if task['validationType'] == 'DEFAULT':
                                        if 'status' not in task:
                                            continue
                                        if task['type'] == 'PROGRESS_TARGET' and task['status'] != 'READY_FOR_CLAIM':
                                            continue
                                        if task['status'] == 'NOT_STARTED':
                                            await self.start_tasks(token=token, task_id=task['id'], task_title=task['title'], username=username)
                                        elif task['status'] == 'READY_FOR_CLAIM':
                                            await self.claim_tasks(token=token, task_id=task['id'], task_title=task['title'], username=username)
        except (aiohttp.ClientResponseError, aiohttp.ContentTypeError) as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Fetching Tasks: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Fetching Tasks: {str(e)} ]{Style.RESET_ALL}")

    async def start_tasks(self, token: str, task_id: str, task_title: str, username: str):
        url = f'https://game-domain.blum.codes/api/v1/tasks/{task_id}/start'
        data = json.dumps({})
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Length': str(len(data))
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    if response.status == 400:
                        return self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ {task_title} Already Started ]{Style.RESET_ALL}"
                        )
                    elif response.status == 500:
                        return self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ Cannot Get {task_title} ]{Style.RESET_ALL}"
                        )
                    elif response.status == 520:
                        return self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ Server Blum Error ]{Style.RESET_ALL}"
                        )
                    else:
                        response.raise_for_status()
                        self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT}[ {task_title} Started ]{Style.RESET_ALL}"
                        )
                        await asyncio.sleep(random.randint(5, 10))
                        return await self.claim_tasks(token=token, task_id=task_id, task_title=task_title, username=username)
        except (aiohttp.ClientResponseError, aiohttp.ContentTypeError) as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Starting Tasks: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Starting Tasks: {str(e)} ]{Style.RESET_ALL}")

    async def claim_tasks(self, token: str, task_id: str, task_title: str, username: str):
        url = f'https://game-domain.blum.codes/api/v1/tasks/{task_id}/claim'
        data = json.dumps({})
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Length': str(len(data))
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    if response.status == 400:
                        return self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ {task_title} Already Claimed ]{Style.RESET_ALL}"
                        )
                    elif response.status == 412:
                        return self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ {task_title} Is Not Done ]{Style.RESET_ALL}"
                        )
                    elif response.status == 500:
                        return self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ Cannot Get {task_title} ]{Style.RESET_ALL}"
                        )
                    elif response.status == 520:
                        return self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ Server Blum Error ]{Style.RESET_ALL}"
                        )
                    else:
                        response.raise_for_status()
                        return self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}[ {task_title} Claimed ]{Style.RESET_ALL}"
                        )
        except (aiohttp.ClientResponseError, aiohttp.ContentTypeError) as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Claiming Tasks: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Claiming Tasks: {str(e)} ]{Style.RESET_ALL}")

    async def balance_friends(self, token: str, username: str):
        url = 'https://user-domain.blum.codes/api/v1/friends/balance'
        headers = {
            **self.headers,
            'Authorization': token
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url, headers=headers) as response:
                    response.raise_for_status()
                    balance_friends = await response.json()
                    if balance_friends['canClaim']:
                        return await self.claim_friends(token=token, username=username)
                    else:
                        if balance_friends['canClaimAt'] is not None:
                            if datetime.now().astimezone() >= datetime.fromtimestamp(balance_friends['canClaimAt'] / 1000).astimezone() and balance_friends['canClaim']:
                                return await self.claim_friends(token=token, username=username)
                            else:
                                formatted_claim_time = datetime.fromtimestamp(balance_friends['canClaimAt'] / 1000).astimezone().strftime('%x %X %Z')
                                return self.print_timestamp(
                                    f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                                    f"{Fore.YELLOW + Style.BRIGHT}[ Referral Reward Can Be Claimed At {formatted_claim_time} ]{Style.RESET_ALL}"
                                )
                        else:
                            return self.print_timestamp(
                                f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT}[ You Did Not Have Referrals ]{Style.RESET_ALL}"
                            )
        except (aiohttp.ClientResponseError, aiohttp.ContentTypeError) as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Fetching Frens: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Fetching Frens: {str(e)} ]{Style.RESET_ALL}")

    async def claim_friends(self, token: str, username: str):
        url = 'https://user-domain.blum.codes/api/v1/friends/claim'
        data = json.dumps({})
        headers = {
            **self.headers,
            'Authorization': token,
            'Content-Length': str(len(data))
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    if response.status == 400:
                        return self.print_timestamp(
                            f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}[ It's Too Early To Claim Friends ]{Style.RESET_ALL}"
                        )

                    response.raise_for_status()
                    claim_friends = await response.json()
                    return self.print_timestamp(
                        f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT}[ Claimed {int(float(claim_friends['claimBalance']))} From Frens ]{Style.RESET_ALL}"
                    )
        except (aiohttp.ClientResponseError, aiohttp.ContentTypeError) as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Claiming Frens: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Claiming Frens: {str(e)} ]{Style.RESET_ALL}")

    async def main(self, queries):
        while True:
            try:
                accounts = await self.auth(queries)
                restart_times = []
                total_balance = 0

                for account in accounts:
                    self.print_timestamp(f"{Fore.WHITE + Style.BRIGHT}[ {account['username']} Home ]{Style.RESET_ALL}")
                    await self.daily_reward(token=account['token'], username=account['username'])
                    await asyncio.sleep(3)

                    user_balance = await self.user_balance(token=account['token'])
                    self.print_timestamp(
                        f"{Fore.CYAN + Style.BRIGHT}[ {account['username']} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT}[ Balance {int(float(user_balance['availableBalance'])) if user_balance else 0} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE + Style.BRIGHT}[ Play Passes {user_balance['playPasses'] if user_balance else 0} ]{Style.RESET_ALL}"
                    )
                    if 'farming' in user_balance:
                        restart_times.append(datetime.fromtimestamp(int(user_balance['farming']['endTime'] / 1000)).astimezone().timestamp())
                        if datetime.now().astimezone() >= datetime.fromtimestamp(user_balance['farming']['endTime'] / 1000).astimezone():
                            await self.claim_farming(token=account['token'], available_balance=user_balance['availableBalance'], username=account['username'])
                        else:
                            formatted_end_time = datetime.fromtimestamp(user_balance['farming']['endTime'] / 1000).astimezone().strftime('%x %X %Z')
                            self.print_timestamp(
                                f"{Fore.CYAN + Style.BRIGHT}[ {account['username']} ]{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT}[ Farming Can Be Claim At {formatted_end_time} ]{Style.RESET_ALL}"
                            )
                    else:
                        await self.start_farming(token=account['token'], available_balance=user_balance['availableBalance'], username=account['username'])

                    await self.balance_friends(token=account['token'], username=account['username'])

                for account in accounts:
                    self.print_timestamp(f"{Fore.WHITE + Style.BRIGHT}[ {account['username']} Play Passes ]{Style.RESET_ALL}")
                    await self.play_game(token=account['token'], username=account['username'])

                for account in accounts:
                    self.print_timestamp(f"{Fore.WHITE + Style.BRIGHT}[ {account['username']} Tasks ]{Style.RESET_ALL}")
                    await self.tasks(token=account['token'], username=account['username'])

                    user_balance = await self.user_balance(token=account['token'])
                    total_balance += int(float(user_balance['availableBalance'])) if user_balance else 0

                if restart_times:
                    now = datetime.now().astimezone().timestamp()
                    future_farming_times = [time - now for time in restart_times if time > now]
                    if future_farming_times:
                        sleep_time = min(future_farming_times) + 30
                    else:
                        sleep_time = 15 * 60
                else:
                    sleep_time = 15 * 60

                self.print_timestamp(
                    f"{Fore.CYAN + Style.BRIGHT}[ Total Account {len(accounts)} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT}[ Total Balance {total_balance} ]{Style.RESET_ALL}"
                )

                timestamp_restart_time = (datetime.now().astimezone() + timedelta(seconds=sleep_time)).strftime('%x %X %Z')
                self.print_timestamp(f"{Fore.CYAN + Style.BRIGHT}[ Restarting At {timestamp_restart_time} ]{Style.RESET_ALL}")

                await asyncio.sleep(sleep_time)
                self.clear_terminal()
            except Exception as e:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
                continue

if __name__ == '__main__':
    try:
        init(autoreset=True)
        blum = Blum()

        queries_files = [f for f in os.listdir() if f.startswith('queries-') and f.endswith('.txt')]
        queries_files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0)

        blum.print_timestamp(f"{Fore.MAGENTA + Style.BRIGHT}[ Select An Option ]{Style.RESET_ALL}")
        blum.print_timestamp(
            f"{Fore.MAGENTA + Style.BRIGHT}[ 1 ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}[ Split Queries ]{Style.RESET_ALL}"
        )
        blum.print_timestamp(
            f"{Fore.MAGENTA + Style.BRIGHT}[ 2 ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}[ Use Existing 'queries-*.txt' ]{Style.RESET_ALL}"
        )

        initial_choice = int(input(
            f"{Fore.CYAN + Style.BRIGHT}[ Enter The Number Corresponding To Your Choice ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
        ))
        if initial_choice == 1:
            blum.print_timestamp(f"{Fore.CYAN + Style.BRIGHT}[ Processing Queries To Generate Files ]{Style.RESET_ALL}")
            blum.process_queries()
            blum.print_timestamp(f"{Fore.CYAN + Style.BRIGHT}[ File Generation Completed ]{Style.RESET_ALL}")

            queries_files = [f for f in os.listdir() if f.startswith('queries-') and f.endswith('.txt')]
            queries_files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0)

            if not queries_files:
                raise FileNotFoundError("No 'queries-*.txt' Files Found")
        elif initial_choice == 2:
            if not queries_files:
                raise FileNotFoundError("No 'queries-*.txt' Files Found")
        else:
            raise ValueError("Invalid Initial Choice. Please Run The Script Again And Choose A Valid Option")

        blum.print_timestamp(f"{Fore.MAGENTA + Style.BRIGHT}[ Select The Queries File To Use ]{Style.RESET_ALL}")
        for i, queries_file in enumerate(queries_files, start=1):
            blum.print_timestamp(
                f"{Fore.MAGENTA + Style.BRIGHT}[ {i} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}[ {queries_file} ]{Style.RESET_ALL}"
            )

        choice = int(input(
            f"{Fore.CYAN + Style.BRIGHT}[ Enter The Number Corresponding To The File You Want To Use ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
        )) - 1
        if choice < 0 or choice >= len(queries_files):
            raise ValueError("Invalid Choice. Please Run The Script Again And Choose A Valid Option")

        selected_file = queries_files[choice]
        queries = blum.load_queries(selected_file)

        asyncio.run(blum.main(queries))
    except (ValueError, IndexError, FileNotFoundError) as e:
        blum.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
    except KeyboardInterrupt:
        sys.exit(0)