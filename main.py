from bs4 import BeautifulSoup
from dataclasses import dataclass, is_dataclass, asdict, field
import requests
import json
import gui

BASE_URL = "https://cv.lv"


def convert_string(text):
    conversion_dict = {
        "ā": "a", "č": "c", "ē": "e", "ģ": "g",
        "ī": "i", "ķ": "k", "ļ": "l", "ņ": "n",
        "š": "s", "ū": "u", "ž": "z"
    }
    output = ""
    for letter in text:
        letter_was_upper = False
        if letter.isupper():
            letter_was_upper = True
            letter = letter.lower()

        if letter in conversion_dict:
            if letter_was_upper:
                output += conversion_dict[letter].upper()
            else:
                output += conversion_dict[letter]
        else:
            if letter_was_upper:
                output += letter.upper()
            else:
                output += letter
    return output


def get_algas(algastring):
    output = []
    split = algastring.split()
    if len(split) > 2:
        output = [int(split[1]), int(split[3])]
    else:
        output = [int(split[1]), int(split[1])]
    return output


# https://stackoverflow.com/questions/51286748/make-the-python-json-encoder-support-pythons-new-dataclasses
class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


page_num = 0

uri = requests.get("https://cv.lv/lv/search?limit=" + str(1000) + "&offset=0" \
      "&categories%5B0%5D=INFORMATION_TECHNOLOGY&fuzzy=true&suitableForRefugees=false&isHourlySalary=false&isRemoteWork=false").text
soup = BeautifulSoup(uri, "lxml")
jobs = soup.find_all("li", class_="jsx-1871295890 jsx-2661613696 vacancies-list__item false")
list_of_jobs = []
for job in jobs:
    job_name = job.find("span", class_="jsx-1507404526 vacancy-item__title").text
    job_name = convert_string(job_name)
    job_name = job_name.upper()
    job_giver = job.find("div", class_="jsx-1507404526 vacancy-item__body").a.text
    job_giver = convert_string(job_giver)
    try:
        algas_teksts = job.find("span", class_="jsx-1507404526 vacancy-item__salary-label").text
    except AttributeError:
        continue
    if "st" in algas_teksts or "." in algas_teksts:
        continue
    min_alga, max_alga = get_algas(algas_teksts)
    link = BASE_URL + job.a["href"]
    list_of_jobs.append(gui.Sludinajums(job_name, job_giver, min_alga, max_alga, link))

list_of_authors = {}
for job in list_of_jobs:
    if job.autors not in list_of_authors:
        list_of_authors[job.autors] = 1
    else:
        list_of_authors[job.autors] += 1

new_authors = []
for key in list_of_authors:
    if list_of_authors[key] >= 5:
        new_authors.append((key, list_of_authors[key]))

new_authors.sort(reverse=True, key=lambda x: x[1])
print(new_authors)

print(f"Sludinajumu skaits {len(list_of_jobs)}")
with open("original.json", "w") as f:
    json_string = json.dumps(list_of_jobs, cls=EnhancedJSONEncoder)
    f.write(json_string)

gui.main(list_of_jobs, new_authors)
