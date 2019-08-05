import urllib.request
from bs4 import BeautifulSoup
import re


class SpecSentencesLoader:
    spec_docs_tc_configuration_id = "Kotlin_Spec_DocsMaster"
    tc_url = "https://teamcity.jetbrains.com"
    tc_path_prefix = "guestAuth/app/rest/builds"
    html_spec_path = "/html/kotlin-spec.html"
    stable_branch = "master"

    paragraph_selectors = ".paragraph, ul, ol"
    section_selectors = "h2, h3, h4, h5"

    def load_raw_html_spec(self, spec_version, build_number):
        html_spec_link =\
            "%s/%s/buildType:(id:%s),number:%s,branch:default:any/artifacts/content/kotlin-spec-%s-%s.zip%s%s"\
            % (self.tc_url, self.tc_path_prefix, self.spec_docs_tc_configuration_id,
               build_number, spec_version, build_number, "%21", self.html_spec_path)

        return urllib.request.urlopen(html_spec_link)

    def get_last_spec_version(self):
        spec_last_build_info_link = "%s/%s/buildType:(id:%s),count:1,status:SUCCESS?branch=%s"\
                                    % (self.tc_url, self.tc_path_prefix,
                                       self.spec_docs_tc_configuration_id, self.stable_branch)

        root_build_info_doc = BeautifulSoup(urllib.request.urlopen(spec_last_build_info_link).read().decode("utf-8"),
                                            "xml")
        artifacts_url = self.tc_url + root_build_info_doc.find("artifacts")["href"]
        artifacts = BeautifulSoup(urllib.request.urlopen(artifacts_url).read().decode("utf-8"), "xml")
        artifact_name = artifacts.findChild().findChild()["href"]
        version_components = re.findall("kotlin-spec-(\d+\.\d+)-([1-9]\d*)\.zip", artifact_name)

        return version_components[0]

    def build_sentences_map(self, spec_html):
        page = BeautifulSoup(spec_html, 'html.parser')
        elements = page.select("%s, %s, .sentence" % (self.section_selectors, self.paragraph_selectors))
        current_sections_path = []
        paragraph_counter = 0
        sentences_by_location = {}

        for element in elements:
            if element.name in self.section_selectors.split(", "):
                while len(current_sections_path) != 0 and int(re.findall('\d+', current_sections_path[-1][0])[0]) >= int(re.findall('\d+', element.name)[0]):
                    current_sections_path.pop()

                current_sections_path.append((element.name, element.attrs["id"]))
                paragraph_counter = 0
            elif (element.has_attr("class") and "paragraph" in element.attrs["class"]) or element.name in "ul, ol".split(", "):
                if element.find_parents("ul") or element.find_parents("ol"):
                    continue
                paragraph_counter += 1
            elif element.has_attr("class") and "sentence" in element.attrs["class"]:
                if not (element.find_parents("ul") or element.find_parents("ol") or element.find_parents("div", {"class": "paragraph"})):
                    continue
                path_joined = ",".join([i[1] for i in current_sections_path]) + "," + str(paragraph_counter)

                if path_joined not in sentences_by_location:
                    sentences_by_location[path_joined] = []

                text = element.getText()
                sentences_by_location[path_joined].append(text)

        return sentences_by_location
