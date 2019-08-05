import glob
import json
import re


class TestsProvider:
    tests_spec_path = "compiler/tests-spec/testData"
    tests_map_filename = "testsMap.json"
    after_test_data_path_regex = re.compile("(?<=testData/)(?P<path_after_test_data>.*?)$")

    def __init__(self, compiler_repo_path):
        self.compiler_repo_path = compiler_repo_path

    def get_tests_map(self):
        tests = {}

        for filename in glob.iglob(
                "{repo_path}/{tests_path}/**/linked/**/{tests_map_filename}".format(
                    repo_path=self.compiler_repo_path,
                    tests_path=self.tests_spec_path,
                    tests_map_filename=self.tests_map_filename
                ),
                recursive=True):
            tests_map = json.loads(open(filename).read())

            for paragraph, paragraphTests in tests_map.items():
                for testType, testTypeTests in paragraphTests.items():
                    for sentence, sentenceTests in testTypeTests.items():
                        for testNumber, test in enumerate(sentenceTests):
                            full_path = "{tests_path}p-{paragraph}/{test_type}/{sentence}.{test_number}.kt".format(
                                tests_path=filename.strip(self.tests_map_filename),
                                paragraph=paragraph,
                                test_type=testType,
                                sentence=sentence,
                                test_number=str(testNumber + 1)
                            )
                            path_after_test_data = self.after_test_data_path_regex.search(full_path)\
                                .group("path_after_test_data")
                            tests[path_after_test_data] = test["specVersion"]

        return tests
