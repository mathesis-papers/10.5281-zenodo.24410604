import argparse
from collections import defaultdict
import hashlib
from itertools import product
import json
from pathlib import Path


def admissible(word, alphabet):
    events = [left for left, right in zip(word, word[1:]) if left == right]
    return all(right == (left + 1) % alphabet for left, right in zip(events, events[1:]))


def phase_counts(alphabet, length):
    if length == 0:
        return 1
    empty, successor, other = alphabet, 0, 0
    for index in range(1, length):
        empty, successor, other = ((alphabet - 1) * empty, other,
                                   empty + alphabet * successor + (alphabet - 2) * other)
    return empty + successor + other


def forward_counts(alphabet, maximum):
    states = {(letter, None): 1 for letter in range(alphabet)}
    counts = [1, alphabet]
    for length in range(2, maximum + 1):
        updated = defaultdict(int)
        for (previous, required), multiplicity in states.items():
            for letter in range(alphabet):
                if letter != previous:
                    updated[letter, required] += multiplicity
                elif required is None or required == letter:
                    updated[letter, (letter + 1) % alphabet] += multiplicity
        states = updated
        counts.append(sum(states.values()))
    return counts


def recurrence_counts(alphabet, maximum):
    values = [1, alphabet, alphabet * alphabet]
    for index in range(3, maximum + 1):
        values.append((2 * alphabet - 3) * values[-1]
                      + (-alphabet * alphabet + 4 * alphabet - 2) * values[-2]
                      - alphabet * (alphabet - 1) * values[-3])
    return values[:maximum + 1]


def add(left, right):
    result = [0] * max(len(left), len(right))
    for index, value in enumerate(left):
        result[index] += value
    for index, value in enumerate(right):
        result[index] += value
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def multiply(left, right):
    result = [0] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            result[left_index + right_index] += left_value * right_value
    return add(result, [0])


def polynomial_rows(maximum):
    values = [[1], [0, 1], [0, 0, 1]]
    for index in range(3, maximum + 1):
        values.append(add(add(multiply([-3, 2], values[-1]),
                              multiply([-2, 4, -1], values[-2])),
                          multiply([0, 1, -1], values[-3])))
    return values


def evaluate(polynomial, value):
    result = 0
    for coefficient in reversed(polynomial):
        result = result * value + coefficient
    return result


def compose_shift(polynomial):
    result = [0]
    for coefficient in reversed(polynomial):
        result = add(multiply(result, [1, 1]), [coefficient])
    return result


def quadratic_multiply(left, right):
    return (left[0] * right[0] + 17 * left[1] * right[1],
            left[0] * right[1] + left[1] * right[0])


def quadratic_power(base, exponent):
    value = (1, 0)
    for index in range(exponent):
        value = quadratic_multiply(value, base)
    return value


def read_bfile(path):
    values = {}
    for line in path.read_text().splitlines():
        text = line.split('#', 1)[0].strip()
        if text:
            index, value = map(int, text.split())
            assert index not in values
            values[index] = value
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--oeis-dir', type=Path)
    parser.add_argument('--output', type=Path)
    arguments = parser.parse_args()
    fixtures = json.loads(Path(__file__).with_name('source-fixtures.json').read_text())
    enumerated_words = 0
    enumeration_cases = 0
    for alphabet in range(2, 9):
        for length in range(7):
            expected = sum(admissible(word, alphabet) for word in product(range(alphabet), repeat=length))
            assert expected == phase_counts(alphabet, length), (alphabet, length)
            enumerated_words += alphabet ** length
            enumeration_cases += 1
    automaton_cases = 0
    for alphabet in range(2, 13):
        forward = forward_counts(alphabet, 80)
        recurrence = recurrence_counts(alphabet, 80)
        denominator = [1, 3 - 2 * alphabet, alphabet * alphabet - 4 * alphabet + 2,
                       alphabet * (alphabet - 1)]
        numerator = [1, 3 - alphabet, 2 - alphabet]
        for length, count in enumerate(forward):
            assert count == phase_counts(alphabet, length) == recurrence[length]
            coefficient = sum(value * forward[length - offset]
                              for offset, value in enumerate(denominator) if offset <= length)
            assert coefficient == (numerator[length] if length < len(numerator) else 0)
            automaton_cases += 1
    original = recurrence_counts(8, 210)
    assert original[1:20] == fixtures['A268943_initial_terms']
    for length, count in enumerate(original):
        minus = quadratic_multiply((153, -37), quadratic_power((3, -1), length))
        plus = quadratic_multiply((153, 37), quadratic_power((3, 1), length))
        assert (minus[0] + plus[0] - 272 * 7 ** length, minus[1] + plus[1]) == (34 * count, 0)
    rows = polynomial_rows(7)
    for length in range(1, 8):
        assert compose_shift(rows[length]) == fixtures['A268944_row_polynomials_in_k'][str(length)]
    assert not admissible((0, 0, 0), 8)
    assert admissible((6, 4, 6, 5, 4), 8)
    assert admissible((7, 7, 0, 0), 8)
    assert not admissible((7, 7, 1, 1), 8)
    for alphabet, examples in fixtures['source_examples'].items():
        assert all(admissible(word, int(alphabet)) for word in examples)
    for length in range(1, 81):
        binary = 3 * 2 ** (length // 2) - 2 if length % 2 == 0 else 2 ** ((length + 3) // 2) - 2
        assert phase_counts(2, length) == binary
    result = {
        'status': 'pass',
        'literal_word_enumeration': {'alphabet_sizes': [2, 8], 'lengths': [0, 6],
                                     'parameter_pairs': enumeration_cases, 'words': enumerated_words},
        'independent_forward_automaton': {'alphabet_sizes': [2, 12], 'lengths': [0, 80],
                                         'parameter_pairs': automaton_cases},
        'eight_letter_radical_exact_arithmetic': {'lengths': [0, 210], 'ring': 'Z[sqrt(17)]'},
        'symbolic_polynomial_rows': {'lengths': [1, 7], 'variable': 'k=q-1'},
        'binary_formula': {'lengths': [1, 80]},
        'source_prefix': {'sequence': 'A268943', 'lengths': [1, 19]},
        'source_examples': {'A268943': 16, 'A268944': 16},
        'scope': 'Finite numerical and exact polynomial checks; the all-length and all-alphabet results have written proofs in note.tex.',
    }
    if arguments.oeis_dir:
        comparisons = {}
        for sequence in ('268943', '268944'):
            path = arguments.oeis_dir / ('b' + sequence + '.txt')
            values = read_bfile(path)
            if sequence == '268943':
                for index, value in values.items():
                    assert value == phase_counts(8, index)
            else:
                diagonal, length = 2, 1
                for expected_index, (index, value) in enumerate(sorted(values.items()), start=1):
                    assert index == expected_index
                    alphabet = diagonal - length + 1
                    assert value == phase_counts(alphabet, length), (index, alphabet, length)
                    length += 1
                    if length == diagonal:
                        diagonal, length = diagonal + 1, 1
            comparisons['A' + sequence] = {'terms': len(values), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        result['complete_source_tables'] = comparisons
    output = json.dumps(result, indent=2, sort_keys=True) + '\n'
    print(output, end='')
    if arguments.output:
        arguments.output.write_text(output)


if __name__ == '__main__':
    main()
