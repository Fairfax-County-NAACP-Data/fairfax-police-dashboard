def text_file(file):
    with open(file) as f:
        text = f.read()

    return text

stops_per_1000_txt = "Number of stops that occur per year (for a group) for every 1000 people (of that group) in the county population. "+\
    "See the About section for details on the population estimates."