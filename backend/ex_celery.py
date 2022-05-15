from tasks import add, f


def test_add():
    result = add.delay(2, 3)
    print(result.ready(), result.get(timeout=1))


def test_f(delay=False):
    print("テスト開始")

    if delay:
        result = f.delay()
        print(result.ready())
    else:
        result = f()
        print(result)

    print("テスト終了")


if __name__ == "__main__":
    test_f(delay=True)
