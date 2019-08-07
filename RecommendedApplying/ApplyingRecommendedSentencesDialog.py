import os
import re

from heapq import nlargest
from SpecSentences.SentencesSimilarityAnalyser import SentencesSimilarityAnalyser
from SpecTests.TestsProvider import TestsProvider


class ApplyingRecommendedSentencesDialog:
    part_test_path_before_sections_regex = re.compile("^(?P<part_test_path>.*?/linked)(?P<remaining_path>.*?)$")
    dirs_in_test_path = re.compile("^(?P<dirs>.*?)/[1-9]\d*\.[1-9]\d*\.kt$")
    test_path_regex = re.compile("linked/(?P<sections>.*?)/p-(?P<paragraph_number>[1-9]\d*)/"
                                 "(?P<test_type>pos|neg)/(?P<sentence_number>[1-9]\d*)\.(?P<test_number>[1-9]\d*)\.kt$")
    test_path_short_regex = re.compile("(?P<sections>.*?)/p-(?P<paragraph_number>[1-9]\d*)/(?P<test_type>pos|neg)/"
                                       "(?P<sentence_number>[1-9]\d*)(?:\.(?P<test_number>[1-9]\d*)\.kt)?$")
    answers = {}
    spec_place_template = " * PLACE: {sections} -> paragraph {paragraph_number} -> sentence {sentence_number}"
    spec_version_template = " * SPEC VERSION: {version}"
    test_number_template = " * NUMBER: {test_number}"
    test_number_regex = r' \* NUMBER: [1-9]\d*'
    select_specific_sentence_regex = re.compile("A(?P<recommendation_number>\d)(?P<apply_to_only_current>!)?")

    def __init__(self, compiler_repo_path, latest_spec_version):
        self.compiler_repo_path = compiler_repo_path
        self.latest_spec_version = latest_spec_version

    @staticmethod
    def get_next_test_number_by_path(path_prefix):
        test_number = 1
        while os.path.isfile("{path_prefix}.{test_number}.kt".format(path_prefix=path_prefix, test_number=test_number)):
            test_number += 1

        return test_number

    def print_and_request_action_for_recommended_sentence(
            self,
            most_similar_sentences,
            test_path_components,
            sentence_location,
            spec_version
    ):
        most_n_similar_sentences = nlargest(
            SentencesSimilarityAnalyser.recommended_sentences_number,
            most_similar_sentences,
            key=lambda t: t[0]
        )

        self.print_recommended_sentence_info(most_n_similar_sentences, test_path_components)
        self.wait_for_answer(most_n_similar_sentences, sentence_location, test_path_components, spec_version)

    def print_recommended_sentence_info(self, most_n_similar_sentences, test_path_components):
        (test_path_prefix, remaining_path, test_type) = test_path_components
        for index, similarity_info in enumerate(most_n_similar_sentences):
            (similarity, new_test_path, sentence_candidate_in_latest_spec) = similarity_info
            new_test_path = new_test_path.replace("/test_type/", "/" + test_type + "/")

            test_path_equals = self.test_path_equals(remaining_path, "/" + new_test_path)

            print("–––> R{index} ({similarity:.6})".format(index=index + 1, similarity=similarity))
            print("        {sentence}".format(sentence=sentence_candidate_in_latest_spec))
            if not test_path_equals:
                print("        ––> Path: {test_path_prefix}/{test_path}.{test_number}.kt".format(
                    test_path_prefix=test_path_prefix,
                    test_path=new_test_path,
                    test_number=self.get_next_test_number_by_path(
                        "{repo_path}/{tests_spec_path}/{test_path_prefix}".format(
                            repo_path=self.compiler_repo_path,
                            tests_spec_path=TestsProvider.tests_spec_path,
                            test_path_prefix=test_path_prefix + "/" + new_test_path
                        )
                    )
                ))
            else:
                print("        ––> Path: the same")

        print("–––––––––––––––––––––––––––––––––––––––––")
        print("A – apply the first recommendation, A{n} – apply n-th recommendation, S – skip, Q – quit.")
        print("Append ! if you want apply it only for the current test.")
        print("Use A0 to apply expected sentence (just update spec version in the test).")

    def get_spec_place_description_by_path(self, path):
        current_test_path_components = self.test_path_regex.search(path)
        return self.spec_place_template.format(
            sections=current_test_path_components.group("sections").replace("/", ", "),
            paragraph_number=current_test_path_components.group("paragraph_number"),
            sentence_number=current_test_path_components.group("sentence_number")
        )

    def just_update_spec_version(self, test_full_path, spec_version):
        if not os.path.isfile(test_full_path):
            return

        test_content = open(test_full_path, "r").read()
        new_test_content = test_content \
            .replace(
                self.spec_version_template.format(version=spec_version),
                self.spec_version_template.format(version=self.latest_spec_version)
            )

        open(test_full_path, "w").write(new_test_content)

    def do_refactor_test(self, test_full_path, test_new_full_path, spec_version, test_number, need_to_move):
        spec_place_to_replace = self.get_spec_place_description_by_path(test_full_path)
        spec_place_replacement = self.get_spec_place_description_by_path(test_new_full_path)

        if not os.path.isfile(test_full_path):
            return

        test_content = open(test_full_path, "r").read()
        new_test_content = test_content\
            .replace(spec_place_to_replace, spec_place_replacement)\
            .replace(
                self.spec_version_template.format(version=spec_version),
                self.spec_version_template.format(version=self.latest_spec_version)
            )

        new_test_content = re.sub(
            self.test_number_template,
            self.test_number_template.format(test_number=test_number),
            new_test_content
        )
        open(test_full_path, "w").write(new_test_content)

        if need_to_move:
            dirs_in_path = self.dirs_in_test_path.search(test_new_full_path).group("dirs")

            if not os.path.exists(dirs_in_path):
                os.makedirs(dirs_in_path)

            os.rename(test_full_path, test_new_full_path)

    def test_path_equals(self, test_path_1, test_path_2):
        test_path_components_1 = self.test_path_short_regex.search(test_path_1)
        test_path_components_2 = self.test_path_short_regex.search(test_path_2)

        for component in ["sections", "paragraph_number", "test_type", "sentence_number"]:
            if test_path_components_1.group(component).lower() != test_path_components_2.group(component).lower():
                return False

        return True

    def get_test_full_path(self, test_path_prefix):
        return "{repo_path}/{tests_spec_path}/{test_path_prefix}".format(
            repo_path=self.compiler_repo_path,
            tests_spec_path=TestsProvider.tests_spec_path,
            test_path_prefix=test_path_prefix
        )

    def apply_recommended(self, recommended_sentence, test_path_components, spec_version):
        (test_path_prefix, test_path_main_part, test_type) = test_path_components
        (_, new_test_path, _) = recommended_sentence
        new_test_path = new_test_path.replace("/test_type/", "/" + test_type + "/")

        test_path_full_prefix = self.get_test_full_path(test_path_prefix)
        test_number = self.get_next_test_number_by_path(
            "{repo_path}/{tests_spec_path}/{test_path_prefix}".format(
                repo_path=self.compiler_repo_path,
                tests_spec_path=TestsProvider.tests_spec_path,
                test_path_prefix=test_path_prefix + "/" + new_test_path
            )
        )

        self.do_refactor_test(
            test_full_path=test_path_full_prefix + test_path_main_part,
            test_new_full_path="{test_prefix}/{test_path}.{test_number}.kt".format(
                test_prefix=test_path_full_prefix,
                test_path=new_test_path,
                test_number=test_number
            ),
            spec_version=spec_version,
            test_number=test_number,
            need_to_move=not self.test_path_equals(test_path_components[1], "/" + new_test_path)
        )

    def wait_for_answer(self, most_n_similar_sentences, sentence_location, test_path_components, spec_version):
        while True:
            if sentence_location in self.answers:
                answer = self.answers[sentence_location]
            else:
                answer = input("Enter your answer: ").replace('\n', "")
            if answer == "A" or answer == "A!":
                most_similar_sentence = most_n_similar_sentences[0]

                self.apply_recommended(most_similar_sentence, test_path_components, spec_version)

                if answer == "A":
                    self.answers[sentence_location] = answer
                break
            elif answer == "S" or answer == "S!":
                if answer == "S":
                    self.answers[sentence_location] = answer
                break
            elif answer == "Q":
                exit(0)
            else:
                applying_n_matches = self.select_specific_sentence_regex.search(answer)
                if applying_n_matches:
                    recommendation_number = int(applying_n_matches.group("recommendation_number"))
                    selected_similar_sentence = most_n_similar_sentences[recommendation_number - 1]

                    if recommendation_number == 0:
                        self.just_update_spec_version(
                            self.get_test_full_path(test_path_components[0]) + test_path_components[1],
                            spec_version
                        )
                    else:
                        self.apply_recommended(selected_similar_sentence, test_path_components, spec_version)

                    if not applying_n_matches.group("apply_to_only_current"):
                        self.answers[sentence_location] = answer

                    break
