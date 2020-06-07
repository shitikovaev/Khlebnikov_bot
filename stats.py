import sqlite3
import matplotlib.pyplot as plt
import matplotlib
import math

DB_PATH = 'resources/meta.db'

# Constructs a pie chart by the list of values and labels.
def makePieChart(labels, sizes, title, filename):
    plt.title(title)
    plt.pie(sizes, labels=labels,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.legend(loc="upper left")
    plt.axis('equal')
    plt.savefig(filename)
    plt.close()

# Construct a chart for cities stats. Contains a column with percentage for every city.
def makeHistChart(x, y, title, ylabel, xlabel, filename):
    x = [item.capitalize() for item in x]
    matplotlib.style.use('ggplot')
    plt.figure(figsize=(20, 10), dpi=200)
    plt.bar(range(len(x)), y)
    plt.title(title)
    plt.ylabel = ylabel
    plt.xlabel = xlabel
    plt.xticks(range(len(x)), x)
    plt.savefig(filename)
    plt.close()

# Counts sum of correct and sum of total for each city, then calculates percentage for each city.
def getCitiesStats():
    conn = sqlite3.connect(DB_PATH)
    data = getFromDB('city', conn)
    data_dict = {}
    for item in data:
        if item[2] != 0:
            if item[0] in data_dict.keys():
                data_dict[item[0]][0] += item[1]
                data_dict[item[0]][1] += item[2]
            else:
                data_dict[item[0]] = [item[1], item[2]]
    ylabel = 'Процент верных по городу'
    xlabel = 'Город'
    makeHistChart(data_dict.keys(), [x[0] / x[1] * 100 for x in data_dict.values()],
                  'Средний процент верных ответов в зависимости от города', ylabel, xlabel, 'resources/img/city_stats.png')

# gets only correct tries and find a share in it for all ages submitted.
def getAgeStats():
    conn = sqlite3.connect(DB_PATH)
    data = getFromDB('age', conn)
    data_dict = {}
    for item in data:
        if item[1] != 0:
            if item[0] in data_dict.keys():
                data_dict[item[0]] += item[1]
            else:
                data_dict[item[0]] = item[1]
    total_correct = math.fsum(data_dict.values())
    data = {x: data_dict[x] / total_correct for x in data_dict}
    makePieChart(data.keys(), data.values(), 'Распределение возрастов среди верных ответов',
                 'resources/img/age_stats.png')


# makes to list by sex: each consists of percentages of correct tries for a user.
# Then counts average percentage for each sex.
def getSexStats():
    conn = sqlite3.connect(DB_PATH)
    data = getFromDB('sex', conn)
    m_percents = [x[1] / x[2] for x in data if x[0] == 'М']
    f_percents = [x[1] / x[2] for x in data if x[0] == 'Ж']
    aver_m = 0
    aver_f = 0
    if m_percents:
        aver_m = math.fsum(m_percents) * 100 / len(m_percents)
    if f_percents:
        aver_f = math.fsum(f_percents) * 100 / len(f_percents)
    labels = ['Мужчины', 'Женщины']
    sizes = [aver_m, aver_f]
    makePieChart(labels, sizes, 'Cредний процент верности ответов по полам', 'resources/img/sex_stats.png')


# sums all correct tries and all total tries
def getTotalStats():
    conn = sqlite3.connect(DB_PATH)
    data = getFromDB('age', conn)
    total_correct = math.fsum([x[1] for x in data])
    total = math.fsum([x[2] for x in data])
    makePieChart(['Верных ответов', 'Неверных попыток'], [total_correct, total - total_correct],
                 'Отношение верных ответов к неверным', 'resources/img/total_stats.png')


def createTables(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS USERS (
                    id INTEGER PRIMARY KEY,
                    sex text,
                    city text,
                    age INTEGER,
                    total INTEGER,
                    correct INTEGER
                    )
    ''')
    conn.commit()


def putUser(meta):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = 1")
    createTables(conn)
    c = conn.cursor()
    c.execute('INSERT INTO USERS VALUES (NULL,?,?,?,?,?)', [meta['sex'], meta['city'], meta['age'],
                                                            meta['total'], meta['correct']])
    conn.commit()


# returns a meta info by category, according correct tries and total tries.
def getFromDB(category, conn):
    c = conn.cursor()
    c.execute(f'SELECT {category}, correct, total FROM USERS ORDER BY 1')
    return c.fetchall()


# getSexStats()
# getCitiesStats()
# getTotalStats()
# getAgeStats()