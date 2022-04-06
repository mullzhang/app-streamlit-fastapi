# demo-streamlit-fastapi

## Build

Build by the following command.
```
docker-compose up --build
```

Access [http://localhost:8080](http://localhost:8080) on your browser.

When building the backend server only,

```
docker image build ./backend -t demo-streamlit-fastapi/backend:latest
docker run -d --rm -p 80:80 -e APP_MODULE=server:app --name backend demo-streamlit-fastapi/backend:latest
```

and then you can submit the test problem as below.

```
python tests/test_demo_streamlit_fastapi.py
```

## References

- [StreamlitとFastAPIで非同期推論MLアプリを作る](https://zenn.dev/dhirooka/articles/f82744d2475b68)