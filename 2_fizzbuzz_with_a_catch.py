what_to_print = {
    (True, False): "A",
    (False, True): "B",
    (True, True): "AB",
}


def keep_going(n):
    n_ = (n % 3 == 0, n % 5 == 0)
    print(what_to_print.get(n_, n))
    return fizzbuzz(n + 1)

dispatch = {
    False: keep_going,
    True: lambda *_: None,
}

def fizzbuzz(num):
    dispatch[num > 100](num)


if __name__ == '__main__':
    fizzbuzz(1)
