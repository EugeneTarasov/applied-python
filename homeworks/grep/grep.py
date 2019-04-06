import argparse
import sys
import re


def output(line):
    print(line)


def output_line(line, pattern_in_line, count, line_number):
    """
    функция обрабатывает строку перед выводом, добавляет номер строки при необходимости
    :param line: исходная строка
    :param pattern_in_line: исходная строка соответствует шаблону поиска
    :param count: номер строки
    :param line_number: флаг, информирующий о необходимости нумеровать строки
    :return: фозвращает строку для в формате вывода
    """
    if line_number:
        if pattern_in_line:
            return f'{count}:{line}'
        else:
            return f'{count}-{line}'
    else:
        return f'{line}'


def pattern_in_line(pattern, line, invert, ignore_case):
    """
    функция проверяет соответствует ли строка шаблону
    :param pattern: шаблон
    :param line: исходная строка
    :param invert: выводить строки, которые НЕ совпадают с шаблоном
    :param ignore_case: не учитывать регистр
    :return: возвращает булево значение
    """
    if ignore_case:
        p_in_line = re.search(pattern.casefold(), line.casefold())
    else:
        p_in_line = re.search(pattern, line)

    if not (invert ^ bool(p_in_line)):
        return False
    else:
        return True


def grep(lines, params):
    count = 0  # считчик строк
    count_pattern = 0  # счетчик строк, совпадающих с шаблоном
    before_context = []  # список, для хранения строк не совпадающих с шаблоном, но которые тоже нужно будет выводить
    after_context = 0  # количество строк, не совпадающих с шаблоном,которые осталось вывести после совпадения
    for line in lines:
        line = line.rstrip()
        count += 1
        if pattern_in_line(params.pattern.replace('?', '.').replace('*', '.*'), line, params.invert, params.ignore_case):
            count_pattern += 1
            if not params.count:
                before_context.reverse()
                while before_context:
                    output(output_line(before_context.pop(), False, count-len(before_context)-1, params.line_number))
                output(output_line(line, True, count, params.line_number))
                if params.context:
                    after_context = params.context
                elif params.after_context:
                    after_context = params.after_context
        elif bool(after_context) & (not params.count):
            output(output_line(line, False, count, params.line_number))
            after_context -= 1
        elif bool(params.context | params.before_context) & (not params.count):
            if params.context:
                if len(before_context) == params.context:
                    before_context.pop(0)
            elif params.before_context:
                if len(before_context) == params.before_context:
                    before_context.pop(0)
            before_context.append(line)
    if params.count:
        output(str(count_pattern))


def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()
