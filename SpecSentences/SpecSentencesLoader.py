import re
import urllib.request

from bs4 import BeautifulSoup
from helpers import spec_version_pattern


class SpecSentencesLoader:
    spec_docs_tc_configuration_id = "Kotlin_Spec_DocsMaster"
    tc_url = "https://teamcity.jetbrains.com"
    tc_path_prefix = "guestAuth/app/rest/builds"
    html_spec_path = "/html/kotlin-spec.html"
    stable_branch = "master"
    artifact_regex = re.compile("kotlin-spec-{spec_version_pattern}\.zip".format(
        spec_version_pattern=spec_version_pattern
    ))

    header_levels = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5}

    sentence_class = "sentence"
    paragraph_class = "paragraph"
    paragraph_ul = "ul"
    paragraph_ol = "ol"
    paragraph_tags = "{ul}, {ol}".format(ul=paragraph_ul, ol=paragraph_ol)
    paragraph_selectors = ".{_class}, {tags}".format(_class=paragraph_class, tags=paragraph_tags)
    section_selectors = "h2, h3, h4, h5"

    def load_raw_html_spec(self, spec_version, build_number):
        html_spec_link = "{tc_url}/{tc_path_prefix}/buildType:(id:{tc_configuration_id}),number:{build_number}," \
                         "branch:default:any/artifacts/content/" \
                         "kotlin-spec-{spec_version}-{build_number}.zip%21{html_spec_path}".format(
            tc_url=self.tc_url,
            tc_path_prefix=self.tc_path_prefix,
            tc_configuration_id=self.spec_docs_tc_configuration_id,
            build_number=build_number,
            spec_version=spec_version,
            html_spec_path=self.html_spec_path
        )

        return urllib.request.urlopen(html_spec_link)

    def get_last_spec_version(self):
        spec_last_build_info_link = "{tc_url}/{tc_path_prefix}/buildType:(id:{tc_configuration_id})," \
                                    "count:1,status:SUCCESS?branch={branch}".format(
            tc_url=self.tc_url,
            tc_path_prefix=self.tc_path_prefix,
            tc_configuration_id=self.spec_docs_tc_configuration_id,
            branch=self.stable_branch
        )

        root_build_info_doc = BeautifulSoup(
            urllib.request.urlopen(spec_last_build_info_link).read().decode("utf-8"), "xml"
        )
        artifacts_url = self.tc_url + root_build_info_doc.find("artifacts")["href"]
        artifacts = BeautifulSoup(
            urllib.request.urlopen(artifacts_url).read().decode("utf-8"), "xml"
        )
        artifact_name = artifacts.findChild().findChild()["href"]

        matches = self.artifact_regex.search(artifact_name)

        return matches.group("version"), matches.group("build_number")

    def build_sentences_map(self, raw_spec_html):
        html_page = BeautifulSoup(raw_spec_html, 'html.parser')
        analysing_elements = html_page.select("{section_selectors}, {paragraph_selectors}, .sentence".format(
            section_selectors=self.section_selectors,
            paragraph_selectors=self.paragraph_selectors
        ))
        sections_hierarchy = []
        paragraph_counter = 0
        sentences_by_location = {}

        for element in analysing_elements:
            # It's section header (e.g. <h2>Expressions</h2>)
            if element.name in self.section_selectors.split(", "):
                while len(sections_hierarchy) != 0\
                        and self.header_levels[sections_hierarchy[-1][0]] >= self.header_levels[element.name]:
                    sections_hierarchy.pop()

                sections_hierarchy.append((element.name, element.attrs["id"]))
                paragraph_counter = 0
            # It's paragraph
            elif (element.has_attr("class") and self.paragraph_class in element.attrs["class"])\
                    or element.name in self.paragraph_tags.split(", "):
                if element.find_parents(self.paragraph_ul) or element.find_parents(self.paragraph_ol):
                    continue

                paragraph_counter += 1
            # It's sentence
            elif element.has_attr("class") and self.sentence_class in element.attrs["class"]:
                if not (element.find_parents(self.paragraph_ul) or element.find_parents(self.paragraph_ol)
                        or element.find_parents("div", {"class": self.paragraph_class})):
                    continue

                sentence_location = "{sections_hierarchy},{paragraph_number}".format(
                    sections_hierarchy=",".join([i[1] for i in sections_hierarchy]),
                    paragraph_number=paragraph_counter
                )

                if sentence_location not in sentences_by_location:
                    sentences_by_location[sentence_location] = []

                sentences_by_location[sentence_location].append(element.getText())

        return sentences_by_location
