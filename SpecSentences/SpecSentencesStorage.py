from SpecSentencesLoader import SpecSentencesLoader


class SpecSentencesStorage:
    specSentences = {}
    latest_key = "latest"
    loader = SpecSentencesLoader()

    def load(self, version_number, build_number):
        version = version_number + build_number
        html_spec = self.loader.load_raw_html_spec(version_number, build_number)
        self.specSentences[version] = self.loader.build_sentences_map(html_spec)

        return self.specSentences[version]

    def get(self, version):
        if version in self.specSentences:
            return self.specSentences[version]

        version_components = version.split('-')

        self.specSentences[version] = self.load(version_components[0], version_components[1])

        return self.specSentences[version]

    def get_latest(self):
        if self.latest_key in self.specSentences:
            return self.specSentences[self.latest_key]

        last_spec_version = self.loader.get_last_spec_version()

        return '-'.join(last_spec_version), self.load(last_spec_version[0], last_spec_version[1])
