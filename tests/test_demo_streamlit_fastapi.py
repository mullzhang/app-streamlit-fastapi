import os
import json
import requests
import time

BACKEND_HOST = os.environ.get('BACKEND_HOST', '127.0.0.1:80')


def main():
    data = dict(numbers=[2, 3, 5], num_partitions=2)
    res = requests.post(f'http://{BACKEND_HOST}/optimize', data=json.dumps(data))
    print(res.text)
    res_json = res.json()
    job_id = res_json['job_id']

    while True:
        res = requests.get(f'http://{BACKEND_HOST}/results/{job_id}')
        res_json = res.json()
        if res_json['status'] == 'COMPLETED':
            break
        else:
            time.sleep(1)
    print(res_json['results'])


if __name__ == '__main__':
    main()