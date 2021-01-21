import pandas as pd
from collections import Counter, OrderedDict


def get_population_by_region():
    # TODO: implement
    return {
        'Schleswig-Holstein': 2.7,
        'Mecklenburg-Vorpommern': 1.6,
        'Hamburg': 1.6,
        'Niedersachsen': 7.4,
        'Bremen': 0.6,
        'Brandenburg': 2.4,
        'Sachsen - Anhalt': 2.2,
        'Berlin': 3.0,
        'Nordrhein - Westfalen': 15.9,
        'Sachsen': 4.0,
        'Hessen': 5.4,
        'Thüringen': 2.2,
        'Rheinland - Pfalz': 3.7,
        'Bayern': 11.4,
        'Baden - Württemberg': 9.5,
        'Saarland': 0.9,
    }


def get_wahlrecht_polls(url='https://www.wahlrecht.de/umfragen/'):
    table = pd.read_html(url)[1].drop(['Unnamed: 1', 'Unnamed: 10'], axis=1).reset_index(drop=True).transpose()
    table.columns = table.iloc[0]
    table = table.drop('Institut')
    table = table.drop('Erhebung', axis=1)
    # beautify table
    table.rename({'Veröffentl.': 'date'})
    table['date'] = pd.to_datetime(table['date'])
    for party in 'CDU/CSU', 'SPD', 'GRÜNE', 'FDP', 'DIE LINKE', 'AfD', 'Sonstige':
        table[party] = table[party].apply(lambda s: float(s.replace('%', '').replace(',', '.')) / 100.)
    return table


def get_latest_poll():
    all_polls = get_wahlrecht_polls()
    selected = all_polls[all_polls['date'] == max(all_polls['date'])]
    return selected


def sainte_lague_rank(n, votes):
    divisor_table = []
    for party, vote in votes.items():
        for i in range(n):
            divisor_table.append((party, vote/(i+0.5)))
    divisor_table.sort(key=lambda x: x[1], reverse=True)
    relevant_seats = divisor_table[:n]
    return dict(Counter(elem[0] for elem in relevant_seats))


def sainte_lague_not_working(n, votes):
    factor = sum(votes.values()) / n
    seats = dict([(a, round(x / factor)) for a, x in votes.items()])
    if sum(seats.values()) > n:
        factor = sum(votes.values()) / (n + 0.5)
    if sum(seats.values()) < n:
        factor = sum(votes.values()) / (n - 0.5)
    seats = dict([(a, round(x / factor)) for a, x in votes.items()])
    if sum(seats.values()) != n:
        raise Exception('stuff')
    return seats


def sainte_lague(n, votes):
    divisor_table = []
    for party, vote in votes.items():
        for i in range(n):
            divisor_table.append((party, vote/(i+0.5)))
    divisor_table.sort(key=lambda x: x[1], reverse=True)
    relevant_seats = divisor_table[n-1:n+1]


def sainte_lague_rank2(n, votes):
    factors = dict([(key, value) for key, value in votes.items()])
    seats = dict([(party, 0) for party in votes])
    while sum(seats.values()) < n:
        key = max(factors, key=factors.get)
        seats[key] += 1
        factors[key] = votes[key] / (2 * seats[key] + 1)
    return seats


def get_initial_seats_per_region():
    sainte_lague(598, get_population_by_region())


def main():
    get_initial_seats_per_region()


if __name__ == '__main__':
    main()
