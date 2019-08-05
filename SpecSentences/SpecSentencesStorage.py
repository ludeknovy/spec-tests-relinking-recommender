import re

from SpecSentences.SpecSentencesLoader import SpecSentencesLoader
from helpers import spec_version_pattern


class SpecSentencesStorage:
    specSentences = {}
    latest_key = "latest"
    loader = SpecSentencesLoader()
    spec_version_regex = re.compile(spec_version_pattern)

    def load(self, version_number, build_number):
        version = version_number + build_number
        html_spec = self.loader.load_raw_html_spec(version_number, build_number)
        self.specSentences[version] = self.loader.build_sentences_map(html_spec)

        return self.specSentences[version]

    def get(self, version):
        if version in self.specSentences:
            return self.specSentences[version]

        matches = self.spec_version_regex.search(version)

        self.specSentences[version] = self.load(matches.group("version"), matches.group("build_number"))

        return self.specSentences[version]

    def get_latest(self):
        if self.latest_key in self.specSentences:
            return self.specSentences[self.latest_key]

        (version, build_number) = self.loader.get_last_spec_version()

        return "{version}-{build_number}".format(version=version, build_number=build_number),\
               self.load(version, build_number)
