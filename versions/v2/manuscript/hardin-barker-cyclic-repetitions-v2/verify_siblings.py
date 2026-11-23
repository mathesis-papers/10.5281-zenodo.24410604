import argparse
from collections import Counter, defaultdict
from itertools import combinations, product
import json
from math import comb
from pathlib import Path

from verify import admissible, phase_counts


def event_labels(word):
    return [left for left, right in zip(word, word[1:]) if left == right]


def relation_counts(alphabet, indegree, maximum):
    counts = [1, alphabet]
    empty, related, other = alphabet, 0, 0
    for length in range(2, maximum + 1):
        empty, related, other = (
            (alphabet - 1) * empty,
            (indegree - 1) * related + indegree * other,
            empty + (alphabet - indegree + 1) * related
            + (alphabet - indegree - 1) * other,
        )
        counts.append(empty + related + other)
    return counts


def event_coefficient(alphabet, indegree, length, events):
    if events == 0:
        return 1 if length == 0 else alphabet * (alphabet - 1) ** (length - 1)
    degree = length - 2 * events
    if degree < 0:
        return 0
    total = 0
    for offset in range(degree + 1):
        left = (1 if offset == 0 else 0) if events == 1 else (
            (-1) ** offset * comb(events + offset - 2, offset))
        right = comb(events + degree - offset, degree - offset) * (
            alphabet - 1) ** (degree - offset)
        total += left * right
    return alphabet * indegree ** (events - 1) * total


def add(left, right):
    result = [0] * max(len(left), len(right))
    for offset, value in enumerate(left):
        result[offset] += value
    for offset, value in enumerate(right):
        result[offset] += value
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def multiply(left, right):
    result = [0] * (len(left) + len(right) - 1)
    for first, first_value in enumerate(left):
        for second, second_value in enumerate(right):
            result[first + second] += first_value * second_value
    return add(result, [0])


def unequal_rows(maximum):
    rows = [[1], [1, 1], [1, 2, 1], [0, 2, 3, 1]]
    for length in range(4, maximum + 1):
        rows.append(add(add(multiply([-1, 2], rows[-1]),
                            multiply([0, 3, -1], rows[-2])),
                        multiply([0, 0, -2], rows[-3])))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    arguments = parser.parse_args()
    relations = 0
    relation_words = 0
    for alphabet in range(2, 5):
        for indegree in range(alphabet):
            incoming_options = [list(combinations(
                [letter for letter in range(alphabet) if letter != target], indegree))
                for target in range(alphabet)]
            expected = relation_counts(alphabet, indegree, 5)
            for incoming in product(*incoming_options):
                relation = {(source, target) for target, sources in enumerate(incoming)
                            for source in sources}
                relations += 1
                for length in range(6):
                    histogram = Counter()
                    for word in product(range(alphabet), repeat=length):
                        labels = event_labels(word)
                        if all(pair in relation for pair in zip(labels, labels[1:])):
                            histogram[len(labels)] += 1
                        relation_words += 1
                    assert sum(histogram.values()) == expected[length]
                    for events in range(length + 1):
                        assert histogram[events] == event_coefficient(
                            alphabet, indegree, length, events)
    cyclic_words = 0
    for alphabet in range(2, 9):
        for length in range(7):
            histogram = Counter()
            for word in product(range(alphabet), repeat=length):
                if admissible(word, alphabet):
                    histogram[len(event_labels(word))] += 1
                cyclic_words += 1
            for events in range(length + 1):
                assert histogram[events] == event_coefficient(alphabet, 1, length, events)
    balanced_words = 0
    for length in range(11):
        for word in product(range(2), repeat=length):
            heights = [0]
            for letter in word:
                heights.append(heights[-1] + 2 * letter - 1)
            assert admissible(word, 2) == (max(heights) - min(heights) <= 2)
            balanced_words += 1
    for length in range(121):
        value = phase_counts(2, length)
        assert value == sum(2 ** min(offset, length - offset)
                            for offset in range(length + 1))
        assert phase_counts(2, length + 2) == 2 * value + 2
        if length:
            assert value - phase_counts(2, length - 1) == 2 ** (length // 2)
    unequal_cases = 0
    for alphabet in range(2, 13):
        values = relation_counts(alphabet, alphabet - 1, 80)
        states = {(letter, None): 1 for letter in range(alphabet)}
        forward = [1, alphabet]
        for length in range(2, 81):
            updated = defaultdict(int)
            for (previous, event), multiplicity in states.items():
                for letter in range(alphabet):
                    if letter != previous:
                        updated[letter, event] += multiplicity
                    elif event is None or event != letter:
                        updated[letter, letter] += multiplicity
            states = updated
            forward.append(sum(states.values()))
        denominator = [1, 3 - 2 * alphabet,
                       (alphabet - 1) * (alphabet - 4), 2 * (alphabet - 1) ** 2]
        numerator = [1, 3 - alphabet, 4 - 2 * alphabet, 2 - alphabet]
        for length, value in enumerate(values):
            assert value == forward[length]
            coefficient = sum(factor * values[length - offset]
                              for offset, factor in enumerate(denominator) if offset <= length)
            assert coefficient == (numerator[length] if length < len(numerator) else 0)
            unequal_cases += 1
        assert values[4] - phase_counts(alphabet, 4) == alphabet * (alphabet - 2)
    expected_rows = {
        1: [1, 1], 2: [1, 2, 1], 3: [0, 2, 3, 1],
        4: [0, 1, 4, 4, 1], 5: [0, -1, 2, 7, 5, 1],
        6: [0, 1, -1, 4, 11, 6, 1], 7: [0, -1, 0, -1, 8, 16, 7, 1],
    }
    rows = unequal_rows(7)
    for length in range(1, 8):
        assert rows[length] == expected_rows[length]
    result = {
        'status': 'pass',
        'regular_relations': {'alphabet_sizes': [2, 4], 'lengths': [0, 5],
                              'relations': relations, 'words': relation_words,
                              'coverage': 'All loopless relations of constant indegree, including nonconstant outdegree; total and event-number counts.'},
        'cyclic_event_counts': {'alphabet_sizes': [2, 8], 'lengths': [0, 6], 'words': cyclic_words},
        'binary_balanced_substrings': {'lengths': [0, 10], 'words': balanced_words},
        'binary_sum_and_recurrences': {'lengths': [0, 120]},
        'fried_rational_function': {'alphabet_sizes': [2, 12], 'lengths': [0, 80],
                                    'parameter_pairs': unequal_cases,
                                    'constant_term': 1,
                                    'positive_index_counts': 'Independent last-letter/last-event automaton.'},
        'A269467_polynomial_rows': {'lengths': [1, 7], 'variable': 'k=q-1'},
        'scope': 'Finite exact enumeration and coefficient identities; the general statements have written proofs in note.tex.'
    }
    encoded = json.dumps(result, indent=2) + '\n'
    if arguments.output:
        arguments.output.write_text(encoded)
    print(encoded, end='')


if __name__ == '__main__':
    main()
