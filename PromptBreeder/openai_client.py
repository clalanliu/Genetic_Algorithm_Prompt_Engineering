from concurrent import futures
import os
import time
from typing import List
from datetime_ import now
import openai
import logging
import tqdm
os.makedirs('exp', exist_ok=True)
logging.basicConfig(filename=f'exp/{now}/log.txt',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


def get_token_price(client):
    if str(client.base_url) == 'https://api.openai.com/v1/':
        return 0.5, 1.5
    elif str(client.base_url) == "https://api.fireworks.ai/inference/v1/":
        return 0.2, 0.2


class Client():
    def __init__(self, api_key, num_workers=10, base_url=None, logger_name=None) -> None:
        self.client = openai.Client(api_key=api_key, base_url=base_url)
        self.logger = logging.getLogger(logger_name)
        self.num_workers = num_workers

    def _generate(self, prompt, **kwargs):
        m = time.time()
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            **kwargs,
        )
        cost = self.log_usage(response, time=time.time()-m)
        self.logger.info(f'[Response] {response.choices[0].message.content}')
        return response.choices[0].message.content, cost

    def log_usage(self, response, time):
        input_rate, output_rate = get_token_price(self.client)
        self.logger.info(
            f'[Token Count] {{"elapsed_time": {time:3.3f}, '
            f'"input_token_count": "{response.usage.prompt_tokens} ({response.usage.prompt_tokens / 1000000 * input_rate :3.5f})", '
            f'"response_token_count": "{response.usage.completion_tokens} ({response.usage.completion_tokens / 1000000 * output_rate :3.5f})"}}')
        return response.usage.prompt_tokens / 1000000 * input_rate + response.usage.completion_tokens / 1000000 * output_rate

    def batch_generate(self, prompts: List[str], **kwargs):
        """A batched version of generate with multiple prompts."""
        with futures.ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            res = list(tqdm.tqdm(executor.map(lambda prompt: self._generate(
                prompt=prompt, **kwargs), prompts), total=len(prompts), desc="Querying"))
        res, cost = [r[0] for r in res], [r[1] for r in res]
        return res, cost
