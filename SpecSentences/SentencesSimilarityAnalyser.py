import sys
import spacy


class SentencesSimilarityAnalyser:
    latest_spec_sentence_vectors = {}
    nlp = spacy.load("en_core_web_lg")
    similarities = {}

    def __init__(self, spec_info):
        (self.latest_spec_version, self.latest_spec_sentences) = spec_info

    @staticmethod
    def print_recommended_sentence_info(similarity, sentence_candidate_in_latest_spec):
        print("---> P ({similarity:.2}): {sentence}".format(
            similarity=similarity,
            sentence=sentence_candidate_in_latest_spec
        ))

    def compute_vectors_by_latest_spec(self):
        for path in self.latest_spec_sentences:
            for sentence in self.latest_spec_sentences[path]:
                if path not in self.latest_spec_sentence_vectors:
                    self.latest_spec_sentence_vectors[path] = []

                self.latest_spec_sentence_vectors[path].append(self.nlp(sentence))

    def print_comparison_results(self, spec_sentences_info, sentence_location, test_path):
        (sections_hierarchy, sentence_number) = sentence_location
        (spec_version, sentences) = spec_sentences_info

        sentence_index = sentence_number - 1

        is_sentence_location_in_actual_sentences_exist =\
            sections_hierarchy in sentences and len(sentences[sections_hierarchy]) > sentence_number
        is_sentence_location_in_expected_sentences_exist = \
            sections_hierarchy in self.latest_spec_sentences \
            and len(self.latest_spec_sentences[sections_hierarchy]) > sentence_number

        if is_sentence_location_in_actual_sentences_exist and is_sentence_location_in_expected_sentences_exist:
            expected_sentence = self.latest_spec_sentences[sections_hierarchy][sentence_index]
            actual_sentence = sentences[sections_hierarchy][sentence_index]
            if expected_sentence == actual_sentence:
                return

        print("------------------------------------------\n{test_path}".format(test_path=test_path))

        if is_sentence_location_in_actual_sentences_exist:
            print("---> E: {expected_sentence}"
                  .format(expected_sentence=sentences[sections_hierarchy][sentence_index]))
        else:
            print("Invalid the spec version in the test (sentence not found in {spec_version})"
                  .format(spec_version=spec_version), file=sys.stderr)
            return

        if is_sentence_location_in_expected_sentences_exist:
            print("---> A: {actual_sentence}"
                  .format(actual_sentence=self.latest_spec_sentences[sections_hierarchy][sentence_index]))
        else:
            print("---> A: sentence not found in {spec_version} spec version"
                  .format(spec_version=self.latest_spec_version), file=sys.stderr)

    def search_most_similar_sentence(self, spec_sentences_info, sentence_location):
        (sections_hierarchy, sentence_number) = sentence_location
        (spec_version, sentences) = spec_sentences_info

        sentence_index = sentence_number - 1
        is_sentence_location_in_actual_sentences_exist = \
            sections_hierarchy in sentences and len(sentences[sections_hierarchy]) > sentence_number
        is_sentence_location_in_expected_sentences_exist = \
            sections_hierarchy in self.latest_spec_sentences \
            and len(self.latest_spec_sentences[sections_hierarchy]) > sentence_number

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

            sentence_vector = self.nlp(sentences[sections_hierarchy][sentence_index])
            another_sentence_with_max_similarity = (0, "")

            for path in self.latest_spec_sentences:
                for index, sentence in enumerate(self.latest_spec_sentences[path]):
                    sentence_vector_in_latest_spec = self.latest_spec_sentence_vectors[path][index]
                    similarity = sentence_vector.similarity(sentence_vector_in_latest_spec)

                    if similarity > another_sentence_with_max_similarity[0]:
                        another_sentence_with_max_similarity = (similarity, sentence)

            self.similarities[similarity_key] = another_sentence_with_max_similarity

            return another_sentence_with_max_similarity
        else:
            return None
