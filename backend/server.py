import logging
import re
import json
import os
from collections import defaultdict
from typing import List
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from pyqubo import Array, Constraint, Placeholder
from neal import SimulatedAnnealingSampler

log_format = '[%(asctime)s][%(filename)s:%(lineno)d] %(message)s'
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=log_format)

app = FastAPI()

RESULT_DIR = '.results'
RESULT_FNAME = 'results.json'


class DataModel(BaseModel):
    numbers: List[int]
    num_partitions: int


def extract_feasible_samples(samples, print_broken=False):
    feasible_samples = []
    for i, sample in enumerate(samples):
        constraints = sample.constraints(only_broken=True)
        if len(constraints) == 0:
            feasible_samples.append(sample)
        elif print_broken:
            logger.info((i, constraints))

    return feasible_samples


def sample_to_partitions(sample):
    def key_to_index(key, var_name='x'):
        match = re.findall(f'{var_name}\[(\d+?)\]\[(\d+?)\]', key)
        return tuple(map(int, match[0]))

    partitions = defaultdict(lambda: [])
    for k, v in sample.sample.items():
        if v == 1:
            i, p = key_to_index(k)
            partitions[p].append(i)
    return dict(partitions)


def optimize(numbers: List[int], num_partitions: int, job_id: str):
    logger.info(numbers)
    logger.info(num_partitions)
    logger.info(job_id)

    x = Array.create('x', (len(numbers), num_partitions), 'BINARY')
    target = sum(numbers) / num_partitions
    variance = sum((sum(number_i * x[i, p] for i, number_i in enumerate(numbers)) - target)**2
                   for p in range(num_partitions))
    onehot = sum((sum(x[i, p] for p in range(num_partitions)) - 1)**2 for i in range(len(numbers)))
    cost_func = variance / num_partitions / max(numbers) + Placeholder('onehot') * Constraint(onehot, 'onehot')
    model = cost_func.compile()

    # TODO: tuning penalty weights automatically
    feed_dict = dict(onehot=1)
    bqm = model.to_bqm(feed_dict=feed_dict)

    # TODO: setting sampler parameters via http request
    logger.info('Sampling')
    sampleset = SimulatedAnnealingSampler().sample(bqm, num_reads=10, num_sweeps=10000).aggregate()
    # import time; time.sleep(5)

    decoded_samples = model.decode_sampleset(sampleset, feed_dict)
    feasible_samples = extract_feasible_samples(decoded_samples)
    if len(feasible_samples) < 1:
        logger.info('No feasible solutions')
        results = None
    else:
        logger.info(f'# of feasible solutions: {len(feasible_samples)}')
        results = list(map(sample_to_partitions, feasible_samples))

    savedir = Path(f'{RESULT_DIR}/{job_id}')
    if not savedir.exists():
        savedir.mkdir(parents=True)

    with open(os.path.join(savedir, RESULT_FNAME), 'w') as f:
        json.dump(results, f)


@app.post('/optimize')
async def post_optimize(data: DataModel, background_tasks: BackgroundTasks = None):
    job_id = datetime.now().strftime("%Y%m%d%H%M%S")
    background_tasks.add_task(
        optimize, numbers=data.numbers, num_partitions=data.num_partitions, job_id=job_id
    )
    return {'job_id': job_id}


@app.get('/results')
async def results():
    file_path = Path(RESULT_DIR)
    if os.path.exists(file_path):
        return list(map(str, file_path.glob('*/*')))
    else:
        return HTTPException(status_code=500, detail="Not found result dir")


@app.get('/result/{job_id}')
async def results(job_id):
    file_path = f'{RESULT_DIR}/{job_id}/{RESULT_FNAME}'
    if os.path.exists(file_path):
        with open(file_path) as f:
            results = json.load(f)
        return dict(status='COMPLETED', results=results)
    else:
        return dict(status='IN_PROGRESS')