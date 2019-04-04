import re
from datetime import datetime
from collections import Counter


def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False,
):
    # preparation

    # Если переданы даты начала и/или конца периода для парсинга,
    # то преобразуем их в объект datetime
    if start_at:
        start_at = datetime.strptime(start_at, '%d/%b/%Y %H:%M:%S')
    else:
        start_at = ''
    if stop_at:
        stop_at = datetime.strptime(stop_at, '%d/%b/%Y %H:%M:%S')
    else:
        stop_at = ''

    # делаем заготовку ркгулярных выражений в зависимости от значений
    # входных параметров
    parameters = dict(
        ignore_files=(r'', r'(/[\w-]+[^\.]\w+/?)'),
        request_type=(request_type, r'.+'),
        start_at=(start_at, datetime(year=1, month=1, day=1)),
        stop_at=(stop_at, datetime.now()),
        ignore_www=(r'', r'(www.)?'),
    )

    # т.к. регулярное выражение очень длинное
    # составляем регулярное выражение для каждого из параметров отдельно
    request_date = r'\[(?P<date>\d{2}/\w{3}/\d{4} \d{2}:\d{2}:\d{2})\]'
    request_type = parameters['request_type'][not request_type]
    request = r'.+://(.+:.+@)?{ignore_www}(?P<host>[^/]*)(:\d+)?(?P<url>(/[^\?]*)?{ignore_files})?(\?.+)?(#.+)?'.format(
        ignore_files=parameters['ignore_files'][ignore_files],
        ignore_www=parameters['ignore_www'][ignore_www],
    )
    protocol = r'.+'
    response_code = r'\d{3}'
    response_time = r'(?P<response_time>\d+)'

    # собираем итоговое регулярное выражение в соответствии со структурой лога
    # [request_date] "request_type request protocol" response_code response_time
    regex = r'{request_date} "{request_type} {request} {protocol}" {response_code} {response_time}'.format(
        request_date=request_date,
        request_type=request_type,
        request=request,
        protocol=protocol,
        response_code=response_code,
        response_time=response_time,
    )
    # end preparation

    # start parse
    with open('log.log', 'r') as log_file:
        urls_count = []  # список для хранения строк, удовлетворяющих условиям поиска
        brt = {}  # словарь, накопительным методом собирает время выполнения запроса
        # парсим файл построчно, результаты кладем в urls_count и brt
        for line in log_file.readlines():
            find = re.search(regex, line)
            if find:
                log_date = datetime.strptime(find.group('date'), '%d/%b/%Y %H:%M:%S')

                if (log_date >= parameters['start_at'][not start_at]) & \
                        (log_date <= parameters['stop_at'][not stop_at]) & \
                        (find['url'] not in ignore_urls):

                    urls_count.append(find['host'] + find['url'])
                    brt[find['host'] + find['url']] = brt.get(find['host'] + find['url'], 0) + int(find['response_time'])
                elif log_date > parameters['stop_at'][not stop_at]:
                    break

    # если необходимо вывести топ 5 самых медленных запросов к серверу,
    # то вычисляем для каждого значения в мловаре brt среднее время запроса
    # результат сохраняем в словарь brt с тем же ключом
    if slow_queries:
        count = dict(Counter(urls_count))
        for key, value in count.items():
            brt[key] = brt[key]//count[key]
        sqc = []  # список для хранения топ 5 самых медленных запросов к серверу
        while len(sqc) < 5 and brt:
            itog = {x: y for x, y in filter(lambda x: brt[x[0]] == max(brt.values()), brt.items())}
            for key, value in itog.items():
                sqc.append(value)
                brt.pop(key)

    # возвращаем результат работы функции
    if slow_queries:
        return sqc
    else:
        return [count[1] for count in Counter(urls_count).most_common(5)]