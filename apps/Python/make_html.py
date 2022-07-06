import os
import csv
import operator
import codecs

data_folder = '/Users/nfinite/Dev/SilverSprint/SilverSprint/apps/SilverSprints/xcode/build/Debug/logs'
data_file_quali = 'wwcwwcw.csv'
data_file_final = '2021_10_02_SilverSprintsRaceLogw.csv'
html_template = '/Users/nfinite/Dev/SilverSprint/SilverSprint/apps/Python/site_template.html'
html_output_file = '/Users/nfinite/Dev/SilverSprint/SilverSprint/apps/Python/site_out.html'
keyword_first_line = 'timestamp'
keyword_open_category = 'open'
categories = ["open", "wtnb"]
events = ["qualifiers", "quarterfinals", "semifinals", "final", "done"]
indices = {
    events[0]: {
        categories[0]: [6, 4, 2, 0, 1, 3, 5, 7],
        categories[1]: [2, 0, 1, 3]
    },
    events[1]: {
        categories[0]: [8, 8, 9, 9, 10, 10, 11, 11],
        categories[1]: [4, 4, 5, 5, 6, 6]
    },
    events[2]: {
        categories[0]: [8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13],
        categories[1]: [4, 4, 5, 5, 6, 6]
    },
    events[3]: {
        categories[0]: [8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14],
        categories[1]: [4, 4, 5, 5, 6, 6]
    },
    events[4]: {
        categories[0]: [8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15],
        categories[1]: [4, 4, 5, 5, 6, 6, 7, 7]
    }
}

sec_template = "{:.2f}s"
table_template = "<tr class={}><td class=\"table_name\">{}</td><td class=\"table_time\">" + sec_template + "</td></tr>\n"
table_colors = ["white", "green", "red"]


def sort_table(table, cols):
    """ sort a table by multiple columns
        table: a list of lists (or tuple of tuples) where each inner list
               represents a row
        cols:  a list (or tuple) specifying the column numbers to sort by
               e.g. (1,0) would sort by column 1, then by column 0
    """
    for col in reversed(cols):
        table = sorted(table, key=operator.itemgetter(col))
    return table


# Prep
data_file_quali = os.path.join(data_folder,data_file_quali)
data_file_final = os.path.join(data_folder,data_file_final)
data = {}

# Read data from CSV file and sort by time & category
data_open = []
data_wtnb = []
with open(data_file_quali, newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for i, row in enumerate(spamreader):
        if not row[0].strip().lower() == keyword_first_line:
            timevec = row[3].strip().split(':')
            timesec = float(60*timevec[0]) + float(timevec[1]) + float(timevec[2])/1000
            cols = [row[2].strip(), timesec]
            if row[4].strip() == keyword_open_category:
                color = table_colors[1] if i % 2 == 0 else table_colors[2]
                data_open.append(cols + [color])
            else:
                color = table_colors[1] if i % 2 == 0 else table_colors[2]
                data_wtnb.append(cols + [color])
data_quali_sorted = {
    categories[0]: sort_table(data_open, (1,0)),
    categories[1]: sort_table(data_wtnb, (1,0))
}
print("Qualifying: Found {} Races in Open Category and {} Races in WTNB Category!".format(len(data_quali_sorted[categories[0]]), len(data_quali_sorted[categories[1]])))

# Read HTML template
f = codecs.open(html_template, 'r')
html = f.read()
f.close()

# Write qualifying times
for cat in categories:
    tablestring = ""
    for i, item in enumerate(data_quali_sorted[cat]):
        color = item[2] if i < len(indices[events[0]][cat]) else table_colors[0]
        tablestring = tablestring + table_template.format(color, item[0], item[1])
    html = html.replace("{table_data_"+ cat + "}", tablestring)

# Finals
event = 0
if os.path.isfile(data_file_final):
    event = 1
    data_final = {
        categories[0]: [],
        categories[1]: []
    }
    with open(data_file_final, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            if not row[0].strip().lower() == keyword_first_line:
                timevec = row[3].strip().split(':')
                timesec = float(60*timevec[0]) + float(timevec[1]) + float(timevec[2])/1000
                cols = [row[2].strip(), timesec]
                if row[4].strip() == keyword_open_category:
                    data_final[categories[0]].append(cols)
                else:
                    data_final[categories[1]].append(cols)
    if len(data_final[categories[0]]) >= 8 and len(data_final[categories[1]]) >= 4:
        event = 2
    if len(data_final[categories[0]]) >= 12 and len(data_final[categories[1]]) >= 6:
        event = 3
    if len(data_final[categories[0]]) >= 14 and len(data_final[categories[1]]) >= 6:
        event = 4
    print("Finals: Found {} Races in Open Category and {} Races in WTNB Category!".format(len(data_final[categories[0]]), len(data_final[categories[1]])))
else:
    print("Finals: Data file not found.")


for cat in categories:
    l = len(indices[events[4]][cat])
    classes = [table_colors[0] for i in range(l)]
    names = ["" for i in range(l)]
    times = ["" for i in range(l)]
    for it, place in enumerate(indices[events[event]][cat]):
        replace_index = place + 1
        if event == 0:
            names[place] = data_quali_sorted[cat][it][0] if len(data_quali_sorted[cat]) > it else ""
        else:
            if len(data_final[cat]) > it:
                # determine winners of finals
                lu = 1 if it % 2 == 0 else -1
                if data_final[cat][it][1] < data_final[cat][it + lu][1]:
                    classes[it] = table_colors[1]
                    names[place] = data_final[cat][it][0]
                else:
                    classes[it + lu] = table_colors[2]
                    names[place] = data_final[cat][it + lu][0]
                names[it] = data_final[cat][it][0]
                times[it] = sec_template.format(data_final[cat][it][1])
            elif it < (8 if cat == 'open' else 4) and event == 1:
                names[it] = data_quali_sorted[cat][indices[events[0]][cat].index(it)][0]

    # write fields
    for i in range(l):
        html = html.replace("{" + "finals_place_{}_class_{}".format(i + 1, cat) + "}", classes[i])
        html = html.replace("{" + "finals_place_{}_name_{}".format(i + 1, cat) + "}", names[i])
        html = html.replace("{" + "finals_place_{}_time_{}".format(i + 1, cat) + "}", times[i])

f = codecs.open(html_output_file, 'w', 'UTF-8')
f.write(html)
f.close()
