from urllib import parse
import json
import requests

from .contest import Contest

class Election():

    def __init__(self, data = None):
        self.name = ""
        self.total_ballots = 0
        self.contests = {}
        if data is not None:
            self.name = data["name"]
            self.total_ballots = data["total_ballots"]

            for contest_name in data["contests"]:
                new_contest = Contest(data["contests"][contest_name])
                self.contests[contest_name] = new_contest

    def read_election_data(self, file_name):
        try:
            parsed = parse.urlparse(file_name)
            if all([parsed.scheme, parsed.netloc, parsed.path]):
                election_data = json.loads(requests.get(file_name).text)
            else:
                with open(file_name, 'r') as f:
                    election_data = json.load(f)
        except:
            raise Exception("Can't read the file")

        return election_data


    def __repr__(self):
        return f"""{{"name": {self.name}, "total_ballots": {self.total_ballots}, "contests" : {self.contests!r}}}"""
