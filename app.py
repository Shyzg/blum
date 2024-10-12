from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from colorama import *
from datetime import datetime, timedelta
from fake_useragent import FakeUserAgent
from faker import Faker
from urllib.parse import parse_qs
import asyncio, json, os, random, re, sys

class Blum:
    def __init__(self) -> None:
        self.faker = Faker()
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
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

    def process_queries(self, lines_per_file: int):
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

    async def generate_token(self, query: str):
        url = 'https://user-domain.blum.codes/api/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP'
        data = json.dumps({'query':query,'referralToken':'ZaPCLmyAt5'})
        headers = {
            **self.headers,
            'Content-Length': str(len(data)),
            'Content-Type': 'application/json'
        }
        try:
            await asyncio.sleep(3)
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                    response.raise_for_status()
                    generate_token = await response.json()
                    user_data = json.loads(parse_qs(query)['user'][0])
                    first_name = user_data['first_name'] if user_data['first_name'] == '' else user_data['username']
                    return (generate_token['token']['refresh'], first_name)
        except (Exception, ClientResponseError) as e:
            self.print_timestamp(
                f"{Fore.YELLOW + Style.BRIGHT}[ Failed To Process {query} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}"
            )
            return None

    async def generate_tokens(self, queries):
        tasks = [self.generate_token(query=query) for query in queries]
        results = await asyncio.gather(*tasks)
        return [result for result in results if result is not None]

    async def daily_reward(self, token: str):
        url = 'https://game-domain.blum.codes/api/v1/daily-reward?offset=-420'
        headers = {
            **self.headers,
            'Authorization': f"Bearer {token}",
            'Content-Length': '0'
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, ssl=False) as response:
                    if response.status == 400:
                        return self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Daily Reward Already Claimed ]{Style.RESET_ALL}")
                    elif response.status in [500, 520]:
                        return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Blum Error While Daily Reward ]{Style.RESET_ALL}")
                    response.raise_for_status()
                    return self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Claimed Daily Reward ]{Style.RESET_ALL}")
        except ClientResponseError as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Daily Reward: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Daily Reward: {str(e)} ]{Style.RESET_ALL}")

    async def my_tribe(self, token: str):
        url = 'https://tribe-domain.blum.codes/api/v1/tribe/my'
        headers = {
            **self.headers,
            'Authorization': f"Bearer {token}"
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers, ssl=False) as response:
                    if response.status == 404:
                        return await self.join_tribe(token=token)
                    response.raise_for_status()
                    my_tribe = await response.json()
                    if my_tribe['shyzagobroadcast'] != 'shyzagobroadcast':
                        return await self.leave_tribe(token=token)
        except (Exception, ClientResponseError):
            return False

    async def join_tribe(self, token: str):
        url = 'https://tribe-domain.blum.codes/api/v1/tribe/ac4f8fcb-c68e-4ed8-afa9-a2ed3e7fab4c/join'
        headers = {
            **self.headers,
            'Authorization': f"Bearer {token}",
            'Content-Length': '0'
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, ssl=False) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError):
            return False

    async def leave_tribe(self, token: str):
        url = 'https://tribe-domain.blum.codes/api/v1/tribe/leave'
        data = json.dumps({})
        headers = {
            **self.headers,
            'Authorization': f"Bearer {token}",
            'Content-Length': str(len(data)),
            'Content-Type': 'application/json'
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                    response.raise_for_status()
                    return await self.join_tribe(token=token)
        except (Exception, ClientResponseError):
            return False

    async def user_balance(self, token: str):
        url = 'https://game-domain.blum.codes/api/v1/user/balance'
        headers = {
            **self.headers,
            'Authorization': f"Bearer {token}"
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers, ssl=False) as response:
                    if response.status in [500, 520]:
                        self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Blum Error While Fetching User Balance ]{Style.RESET_ALL}")
                        return None
                    response.raise_for_status()
                    return await response.json()
        except ClientResponseError as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Fetching User Balance: {str(e)} ]{Style.RESET_ALL}")
            return None
        except Exception as e:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Fetching User Balance: {str(e)} ]{Style.RESET_ALL}")
            return None

    async def start_farming(self, token: str, available_balance: str):
        url = 'https://game-domain.blum.codes/api/v1/farming/start'
        headers = {
            **self.headers,
            'Authorization': f"Bearer {token}",
            'Content-Length': '0'
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, ssl=False) as response:
                    if response.status in [500, 520]:
                        return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Blum Error While Start Farming ]{Style.RESET_ALL}")
                    response.raise_for_status()
                    start_farming = await response.json()
                    if datetime.now().astimezone() >= datetime.fromtimestamp(start_farming['endTime'] / 1000).astimezone():
                        return await self.claim_farming(token=token, available_balance=available_balance)
                    return self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Farming Started, And Can Be Claim At {datetime.fromtimestamp(start_farming['endTime'] / 1000).astimezone().strftime('%x %X %Z')} ]{Style.RESET_ALL}")
        except ClientResponseError as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Start Farming: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Start Farming: {str(e)} ]{Style.RESET_ALL}")

    async def claim_farming(self, token: str, available_balance: str):
        url = 'https://game-domain.blum.codes/api/v1/farming/claim'
        headers = {
            **self.headers,
            'Authorization': f"Bearer {token}",
            'Content-Length': '0'
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, ssl=False) as response:
                    if response.status == 412:
                        self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Need To Start Farming ]{Style.RESET_ALL}")
                        return await self.start_farming(token=token, available_balance=available_balance)
                    elif response.status == 425:
                        return self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ It's Too Early To Claim Farming ]{Style.RESET_ALL}")
                    elif response.status in [500, 520]:
                        return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Blum Error While Claim Farming ]{Style.RESET_ALL}")
                    response.raise_for_status()
                    claim_farming = await response.json()
                    self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ You\'ve Got {int(float(claim_farming['availableBalance'])) - int(float(available_balance))} From Farming ]{Style.RESET_ALL}")
                    return await self.start_farming(token=token, available_balance=available_balance)
        except ClientResponseError as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Claim Farming: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Claim Farming: {str(e)} ]{Style.RESET_ALL}")

    async def dogs_drop(self, token: str):
        url = 'https://game-domain.blum.codes/api/v2/game/eligibility/dogs_drop'
        headers = {
            **self.headers,
            'Authorization': f"Bearer {token}"
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers, ssl=False) as response:
                    response.raise_for_status()
                    dogs_drop = await response.json()
                    if dogs_drop['eligible']:
                        return self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Your Account Is Eligible To Dogs Drop ]{Style.RESET_ALL}")
                    return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Your Account Isn\'t Eligible To Dogs Drop ]{Style.RESET_ALL}")
        except ClientResponseError as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Play Passes: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Play Passes: {str(e)} ]{Style.RESET_ALL}")

    async def play_game(self, token: str):
        url = 'https://game-domain.blum.codes/api/v2/game/play'
        headers = {
            **self.headers,
            'Authorization': f"Bearer {token}",
            'Content-Length': '0'
        }
        while True:
            try:
                async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                    async with session.post(url=url, headers=headers, ssl=False) as response:
                        if response.status == 400:
                            return self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Not Enough Play Passes ]{Style.RESET_ALL}")
                        elif response.status in [500, 520]:
                            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Blum Error While Play Passes ]{Style.RESET_ALL}")
                        response.raise_for_status()
                        game_play = await response.json()
                        self.print_timestamp(
                            f"{Fore.BLUE + Style.BRIGHT}[ Game Started ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT}[ Please Wait ~30 Seconds ]{Style.RESET_ALL}"
                        )
                        await asyncio.sleep(30 + random.randint(3, 5))
                        await self.claim_game(token=token, game_id=game_play['gameId'], points=random.randint(1000, 1001))
            except ClientResponseError as e:
                return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Play Passes: {str(e)} ]{Style.RESET_ALL}")
            except Exception as e:
                return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Play Passes: {str(e)} ]{Style.RESET_ALL}")

    async def claim_game(self, token: str, game_id: str, points: int):
        url = 'https://game-domain.blum.codes/api/v2/game/claim'
        while True:
            data = json.dumps({'gameId':game_id,'points':points})
            headers = {
                **self.headers,
                'Authorization': f"Bearer {token}",
                'Content-Length': str(len(data)),
                'Content-Type': 'application/json'
            }
            try:
                async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                    async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                        if response.status == 404:
                            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Game Session Not Found ]{Style.RESET_ALL}")
                        elif response.status in [500, 520]:
                            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Blum Error While Claim Play Passes ]{Style.RESET_ALL}")
                        response.raise_for_status()
                        return self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ Game Claimed ]{Style.RESET_ALL}")
            except ClientResponseError as e:
                return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Claim Passes: {str(e)} ]{Style.RESET_ALL}")
            except Exception as e:
                return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Claim Passes: {str(e)} ]{Style.RESET_ALL}")

    async def answers(self):
        url = 'https://raw.githubusercontent.com/Shyzg/answer/refs/heads/main/answer.json'
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url, ssl=False) as response:
                    response.raise_for_status()
                    return json.loads(await response.text())
        except (Exception, ClientResponseError):
            return None

    async def tasks(self, token: str):
        url = 'https://earn-domain.blum.codes/api/v1/tasks'
        headers = {
            **self.headers,
            'Authorization': f"Bearer {token}"
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers, ssl=False) as response:
                    if response.status in [500, 520]:
                        return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Blum Error While Start Tasks ]{Style.RESET_ALL}")
                    response.raise_for_status()
                    tasks = await response.json()
                    await self.process_tasks(token, tasks)
        except ClientResponseError as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Fetching Tasks: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Fetching Tasks: {str(e)} ]{Style.RESET_ALL}")

    async def process_tasks(self, token: str, tasks: list):
        for category in tasks:
            await self.process_task_items(token, category.get('tasks', []))
            for section in category.get('subSections', []):
                await self.process_task_items(token, section.get('tasks', []))
            for task in category.get('tasks', []):
                if 'subTasks' in task:
                    await self.process_task_items(token, task['subTasks'])

    async def process_task_items(self, token: str, tasks: list):
        for task in tasks:
            if 'status' in task:
                if task['status'] == 'NOT_STARTED':
                    await self.start_tasks(token=token, task_id=task['id'], task_title=task['title'], task_reward=task['reward'])
                elif task['status'] == 'READY_FOR_CLAIM':
                    await self.claim_tasks(token=token, task_id=task['id'], task_title=task['title'], task_reward=task['reward'])
                elif task['status'] == 'READY_FOR_VERIFY':
                    answers = await self.answers()
                    if answers is not None:
                        if task['title'] in answers['blum']:
                            answer = answers['blum'][task['title']]
                            await self.validate_tasks(token=token, task_id=task['id'], task_title=task['title'], task_reward=task['reward'], payload={'keyword':answer})

    async def start_tasks(self, token: str, task_id: str, task_title: str, task_reward: str):
        url = f'https://earn-domain.blum.codes/api/v1/tasks/{task_id}/start'
        headers = {
            **self.headers,
            'Authorization': f"Bearer {token}",
            'Content-Length': '0'
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, ssl=False) as response:
                    if response.status in [400, 412]: return
                    elif response.status in [500, 520]:
                        return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Blum Error While Start Tasks ]{Style.RESET_ALL}")
                    response.raise_for_status()
                    self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ {task_title} Started ]{Style.RESET_ALL}")
                    await asyncio.sleep(random.randint(5, 10))
                    return await self.claim_tasks(token=token, task_id=task_id, task_title=task_title, task_reward=task_reward)
        except ClientResponseError as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Start Tasks: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Start Tasks: {str(e)} ]{Style.RESET_ALL}")

    async def claim_tasks(self, token: str, task_id: str, task_title: str, task_reward: str):
        url = f'https://earn-domain.blum.codes/api/v1/tasks/{task_id}/claim'
        headers = {
            **self.headers,
            'Authorization': f"Bearer {token}",
            'Content-Length': '0'
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, ssl=False) as response:
                    if response.status in [400, 412]: return
                    elif response.status in [500, 520]:
                        return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Blum Error While Claim Tasks ]{Style.RESET_ALL}")
                    response.raise_for_status()
                    return self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ You\'ve Got {task_reward} From {task_title} ]{Style.RESET_ALL}")
        except ClientResponseError as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Claim Tasks: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Claim Tasks: {str(e)} ]{Style.RESET_ALL}")

    async def validate_tasks(self, token: str, task_id: str, task_title: str, task_reward: str, payload: dict):
        url = f'https://earn-domain.blum.codes/api/v1/tasks/{task_id}/validate'
        data = json.dumps(payload)
        headers = {
            **self.headers,
            'Authorization': f"Bearer {token}",
            'Content-Length': str(len(data)),
            'Content-Type': 'application/json'
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                    if response.status in [400, 412]: return
                    elif response.status in [500, 520]:
                        return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Blum Error While Validate Tasks ]{Style.RESET_ALL}")
                    response.raise_for_status()
                    validate_tasks = await response.json()
                    if validate_tasks['status'] == 'READY_FOR_CLAIM':
                        await self.claim_tasks(token=token, task_id=task_id, task_title=task_title, task_reward=task_reward)
        except ClientResponseError as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Validate Tasks: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Validate Tasks: {str(e)} ]{Style.RESET_ALL}")

    async def balance_friends(self, token: str):
        url = 'https://user-domain.blum.codes/api/v1/friends/balance'
        headers = {
            **self.headers,
            'Authorization': f"Bearer {token}"
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers, ssl=False) as response:
                    if response.status in [500, 520]:
                        return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Blum Error While Fetching Frens ]{Style.RESET_ALL}")
                    response.raise_for_status()
                    balance_friends = await response.json()
                    if balance_friends['canClaim']:
                        return await self.claim_friends(token=token)
        except ClientResponseError as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Fetching Frens: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Fetching Frens: {str(e)} ]{Style.RESET_ALL}")

    async def claim_friends(self, token: str):
        url = 'https://user-domain.blum.codes/api/v1/friends/claim'
        headers = {
            **self.headers,
            'Authorization': f"Bearer {token}",
            'Content-Length': '0'
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, ssl=False) as response:
                    if response.status == 400:
                        return self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ It's Too Early To Claim Friends ]{Style.RESET_ALL}")
                    elif response.status in [500, 520]:
                        return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Blum Error While Claim Frens ]{Style.RESET_ALL}")
                    response.raise_for_status()
                    claim_friends = await response.json()
                    return self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ You\'ve Got {int(float(claim_friends['claimBalance']))} From Frens ]{Style.RESET_ALL}")
        except ClientResponseError as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Claim Frens: {str(e)} ]{Style.RESET_ALL}")
        except Exception as e:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Claim Frens: {str(e)} ]{Style.RESET_ALL}")

    async def main(self, queries):
        while True:
            try:
                accounts = await self.generate_tokens(queries)
                restart_times = []
                total_balance = 0

                for (token, username) in accounts:
                    self.print_timestamp(
                        f"{Fore.WHITE + Style.BRIGHT}[ Home ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                    )
                    await self.my_tribe(token=token)
                    await self.daily_reward(token=token)
                    await self.dogs_drop(token=token)
                    user_balance = await self.user_balance(token=token)
                    if user_balance is not None:
                        self.print_timestamp(
                            f"{Fore.GREEN + Style.BRIGHT}[ Balance {int(float(user_balance['availableBalance']))} ]{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT}[ Play Passes {user_balance['playPasses']} ]{Style.RESET_ALL}"
                        )
                        if 'farming' in user_balance:
                            if datetime.now().astimezone() >= datetime.fromtimestamp(user_balance['farming']['endTime'] / 1000).astimezone():
                                await self.claim_farming(token=token, available_balance=user_balance['availableBalance'])
                            else:
                                restart_times.append(datetime.fromtimestamp(int(user_balance['farming']['endTime'] / 1000)).astimezone().timestamp())
                                self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Farming Can Be Claim At {datetime.fromtimestamp(user_balance['farming']['endTime'] / 1000).astimezone().strftime('%x %X %Z')} ]{Style.RESET_ALL}")
                        else:
                            await self.start_farming(token=token, available_balance=user_balance['availableBalance'])
                    await self.balance_friends(token=token)

                for (token, username) in accounts:
                    self.print_timestamp(
                        f"{Fore.WHITE + Style.BRIGHT}[ Tasks ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}[ {username} ]{Style.RESET_ALL}"
                    )
                    await self.tasks(token=token)
                    user_balance = await self.user_balance(token=token)
                    total_balance += int(float(user_balance['availableBalance'])) if user_balance else 0

                if restart_times:
                    future_farming_times = [time - datetime.now().astimezone().timestamp() for time in restart_times if time > datetime.now().astimezone().timestamp()]
                    if future_farming_times:
                        sleep_time = min(future_farming_times)
                    else:
                        sleep_time = 15 * 60
                else:
                    sleep_time = 15 * 60

                self.print_timestamp(
                    f"{Fore.CYAN + Style.BRIGHT}[ Total Account {len(accounts)} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT}[ Total Balance {total_balance} ]{Style.RESET_ALL}"
                )
                self.print_timestamp(f"{Fore.CYAN + Style.BRIGHT}[ Restarting At {(datetime.now().astimezone() + timedelta(seconds=sleep_time)).strftime('%x %X %Z')} ]{Style.RESET_ALL}")

                await asyncio.sleep(sleep_time)
                self.clear_terminal()
            except Exception as e:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
                continue

if __name__ == '__main__':
    try:
        if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        init(autoreset=True)
        blum = Blum()

        queries_files = [f for f in os.listdir() if f.startswith('queries-') and f.endswith('.txt')]
        queries_files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0)

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
        blum.print_timestamp(
            f"{Fore.MAGENTA + Style.BRIGHT}[ 3 ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}[ Use 'queries.txt' Without Splitting ]{Style.RESET_ALL}"
        )
        initial_choice = int(input(
            f"{Fore.BLUE + Style.BRIGHT}[ {datetime.now().astimezone().strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.YELLOW + Style.BRIGHT}[ Select An Option ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
        ))

        if initial_choice == 1:
            accounts = int(input(
                f"{Fore.YELLOW + Style.BRIGHT}[ How Much Account That You Want To Process Each Terminal ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            ))
            blum.print_timestamp(f"{Fore.CYAN + Style.BRIGHT}[ Processing Queries To Generate Files ]{Style.RESET_ALL}")
            blum.process_queries(lines_per_file=accounts)

            queries_files = [f for f in os.listdir() if f.startswith('queries-') and f.endswith('.txt')]
            queries_files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0)

            if not queries_files:
                raise FileNotFoundError("No 'queries-*.txt' Files Found")
        elif initial_choice == 2:
            if not queries_files:
                raise FileNotFoundError("No 'queries-*.txt' Files Found")
        elif initial_choice == 3:
            queries = [line.strip() for line in open('queries.txt') if line.strip()]
        else:
            raise ValueError("Invalid Initial Choice. Please Run The Script Again And Choose A Valid Option")

        if initial_choice in [1, 2]:
            blum.print_timestamp(f"{Fore.MAGENTA + Style.BRIGHT}[ Select The Queries File To Use ]{Style.RESET_ALL}")
            for i, queries_file in enumerate(queries_files, start=1):
                blum.print_timestamp(
                    f"{Fore.MAGENTA + Style.BRIGHT}[ {i} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}[ {queries_file} ]{Style.RESET_ALL}"
                )

            choice = int(input(
                f"{Fore.BLUE + Style.BRIGHT}[ {datetime.now().astimezone().strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}[ Select 'queries-*.txt' File ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            )) - 1
            if choice < 0 or choice >= len(queries_files):
                raise ValueError("Invalid Choice. Please Run The Script Again And Choose A Valid Option")

            selected_file = queries_files[choice]
            queries = blum.load_queries(selected_file)
        asyncio.run(blum.main(queries=queries))
    except (ValueError, IndexError, FileNotFoundError) as e:
        blum.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
    except KeyboardInterrupt:
        sys.exit(0)