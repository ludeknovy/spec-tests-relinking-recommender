import sys
import spacy
import warnings
import os

from heapq import heappush, nlargest, nsmallest, heapreplace

warnings.filterwarnings("ignore", category=UserWarning)


class SentencesSimilarityAnalyser:
    latest_spec_sentence_vectors = {}
    nlp = spacy.load("en_core_web_lg")
    similarities = {}
    recommended_sentences_number = 3

    def __init__(self, spec_info):
        (self.latest_spec_version, self.latest_spec_sentences) = spec_info

    def compute_vectors_by_latest_spec(self):
        for path in self.latest_spec_sentences:
            for sentence in self.latest_spec_sentences[path]:
                if path not in self.latest_spec_sentence_vectors:
                    self.latest_spec_sentence_vectors[path] = []

                self.latest_spec_sentence_vectors[path].append(self.nlp(sentence))

    def print_comparison_results(self, spec_sentences_info, sentence_location, test_path):
        (sections_hierarchy, sentence_number, _) = sentence_location
        (spec_version, sentences) = spec_sentences_info

        sentence_index = sentence_number - 1

        is_sentence_location_in_actual_sentences_exist =\
            sections_hierarchy in sentences and len(sentences[sections_hierarchy]) >= sentence_number
        is_sentence_location_in_expected_sentences_exist = \
            sections_hierarchy in self.latest_spec_sentences \
            and len(self.latest_spec_sentences[sections_hierarchy]) >= sentence_number

        if is_sentence_location_in_actual_sentences_exist and is_sentence_location_in_expected_sentences_exist:
            expected_sentence = self.latest_spec_sentences[sections_hierarchy][sentence_index]
            actual_sentence = sentences[sections_hierarchy][sentence_index]
            if expected_sentence == actual_sentence:
                return

        print("=========================================")
        print("Comparing by spec {spec_version_1} (actual) to {spec_version_2} (expected)"
              .format(test_path=test_path, spec_version_1=spec_version, spec_version_2=self.latest_spec_version))
        print("–––––––––––––––––––––––––––––––––––––––––")

        if is_sentence_location_in_actual_sentences_exist:
            print("–––> A: {actual_sentence}"
                  .format(actual_sentence=sentences[sections_hierarchy][sentence_index]))
            print("        ––> Path: {test_path}".format(test_path=test_path))
        else:
            print("Invalid the spec version in the test (sentence not found in {spec_version})"
                  .format(spec_version=spec_version), file=sys.stderr)
            print("        ––> Path: {test_path}".format(test_path=test_path))
            return

        if is_sentence_location_in_expected_sentences_exist:
            print("–––> E: {expected_sentence}"
                  .format(expected_sentence=self.latest_spec_sentences[sections_hierarchy][sentence_index]))
        else:
            print("–––> E: sentence not found in {spec_version} spec version"
                  .format(spec_version=self.latest_spec_version), file=sys.stderr)

    def search_most_similar_sentences(self, spec_sentences_info, sentence_location):
        (sections_hierarchy, sentence_number, test_type) = sentence_location
        (spec_version, sentences) = spec_sentences_info

        sentence_index = sentence_number - 1
        is_sentence_location_in_actual_sentences_exist = \
            sections_hierarchy in sentences and len(sentences[sections_hierarchy]) >= sentence_number
        is_sentence_location_in_expected_sentences_exist = \
            sections_hierarchy in self.latest_spec_sentences \
            and len(self.latest_spec_sentences[sections_hierarchy]) >= sentence_number

        if is_sentence_location_in_actual_sentences_exist and is_sentence_location_in_expected_sentences_exist:
            expected_sentence = self.latest_spec_sentences[sections_hierarchy][sentence_index]
            actual_sentence = sentences[sections_hierarchy][sentence_index]

            if expected_sentence == actual_sentence:
                return

            similarity_key = "{sections},{sentence_index}".format(
                sections=sections_hierarchy,
                sentence_index=str(sentence_index)
            )

            if similarity_key in self.similarities:
                return self.similarities[similarity_key]

            sentence = sentences[sections_hierarchy][sentence_index]

            sentence_vector = self.nlp(sentence)

            most_similar_five_sentences = []

            for sentence_location in self.latest_spec_sentences:
                for index, sentence in enumerate(self.latest_spec_sentences[sentence_location]):
                    sentence_vector_in_latest_spec = self.latest_spec_sentence_vectors[sentence_location][index]
                    similarity = sentence_vector.similarity(sentence_vector_in_latest_spec)

                    location_components = sentence_location.split(',')
                    new_test_path = "{sections}/p-{paragraph_number}/test_type/{sentence_number}".format(
                        sections='/'.join(location_components[0:-1]),
                        paragraph_number=location_components[-1],
                        sentence_number=str(index + 1)
                    )

                    if len(most_similar_five_sentences) > self.recommended_sentences_number:
                        min_similarity = nsmallest(1, most_similar_five_sentences, key=lambda t: t[0])[0]
                        if similarity > min_similarity[0]:
                            heapreplace(most_similar_five_sentences, (similarity, new_test_path, sentence))
                    else:
                        heappush(most_similar_five_sentences, (similarity, new_test_path, sentence))

            self.similarities[similarity_key] = most_similar_five_sentences

            return most_similar_five_sentences
        else:
            return None
