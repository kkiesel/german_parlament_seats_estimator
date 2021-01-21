import pandas as pd
from collections import Counter, OrderedDict
import random
import matplotlib.pyplot as plt
from enum import Enum

random.seed(0)


class Region(Enum):
    SE = 'Schleswig-Holstein'
    MV = 'Mecklenburg-Vorpommern'
    HH = 'Hamburg'
    NS = 'Niedersachsen'
    HB = 'Bremen'
    BR = 'Brandenburg'
    ST = 'Sachsen - Anhalt'
    BE = 'Berlin'
    NR = 'Nordrhein - Westfalen'
    SA = 'Sachsen'
    HE = 'Hessen'
    TU = 'Thüringen'
    RP = 'Rheinland - Pfalz'
    BA = 'Bayern'
    BW = 'Baden - Württemberg'
    SL = 'Saarland'


class Party(Enum):
    CDU = 'CDU/CSU'
    SPD = 'SPD'
    GR = 'Bündnis 90/Die Grünen'
    LINKE = 'Die Linke'
    AFD = 'AfD'
    FDP = 'FDP'
    XXX = 'Sonstige'


def get_population_by_region():
    # TODO: implement
    return OrderedDict([
        ('Schleswig-Holstein', 2.7),
        ('Mecklenburg-Vorpommern', 1.6),
        ('Hamburg', 1.6),
        ('Niedersachsen', 7.4),
        ('Bremen', 0.6),
        ('Brandenburg', 2.4),
        ('Sachsen - Anhalt', 2.2),
        ('Berlin', 3.0),
        ('Nordrhein - Westfalen', 15.9),
        ('Sachsen', 4.0),
        ('Hessen', 5.4),
        ('Thüringen', 2.2),
        ('Rheinland - Pfalz', 3.7),
        ('Bayern', 11.4),
        ('Baden - Württemberg', 9.5),
        ('Saarland', 0.9),
    ])


def get_wahlrecht_polls(url='https://www.wahlrecht.de/umfragen/'):
    table = pd.read_html(url)[1].drop(['Unnamed: 1', 'Unnamed: 10'], axis=1).reset_index(drop=True).transpose()
    table.columns = table.iloc[0]
    table = table.drop('Institut')
    table = table.drop('Erhebung', axis=1)
    # beautify table
    table.rename(columns={'Veröffentl.': 'date'}, inplace=True)
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


def sainte_lague(n, votes):
    factors = dict([(key, value) for key, value in votes.items()])
    seats = OrderedDict([(party, 0) for party in votes])
    while sum(seats.values()) < n:
        key = max(factors, key=factors.get)
        seats[key] += 1
        factors[key] = votes[key] / (2 * seats[key] + 1)
    return seats


def get_initial_seats_per_region():
    return sainte_lague(598, get_population_by_region())


def get_polls_per_region(regions, country_polls):
    result = pd.DataFrame()
    for region in regions:
        country_polls['region'] = region
        result = pd.concat([result, country_polls])
    return result

def get_polls_modified_by_green_uncertainty(polls, uncertainty_green):
    poll_dict = polls.iloc[0].to_dict()
    new_green = random.gauss(poll_dict['GRÜNE'], uncertainty_green)
    scale = new_green / poll_dict['GRÜNE']
    new_polls = dict([(party, poll_dict[party]/scale) for party in ['CDU/CSU', 'SPD', 'FDP', 'DIE LINKE', 'AfD']])
    new_polls['GRÜNE'] = new_green
    return new_polls




def main():
    #initial_seats_per_region = get_initial_seats_per_region()
    #polls_per_region = get_polls_per_region(initial_seats_per_region.keys(), get_latest_poll())
    # hessen
    green_seats_hessen = []
    latest_polls = get_latest_poll()
    while len(green_seats_hessen) < 1000:
        seats = sainte_lague(43, get_polls_modified_by_green_uncertainty(latest_polls, 0.02))
        green_seats_hessen.append(seats['GRÜNE'])
    print(green_seats_hessen)
    plt.hist(green_seats_hessen, [x-0.5 for x in range(5,20)])
    plt.show()
    pass


if __name__ == '__main__':
    main()
