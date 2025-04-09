"""
A script to update the form pages and translation files in the LIME EMR
"""

from dotenv import load_dotenv, find_dotenv
import os
import json

load_dotenv(find_dotenv())

SHEETS_TO_PREVIEW = "SHEETS_TO_PREVIEW"
PATH_TO_FORM_FILES = "PATH_TO_FORM_FILES"
PATH_TO_TRANSLATION_FILES = "PATH_TO_TRANSLATION_FILES"
GENERATED_FORM_PATH = "generated_form_schemas/"
CURRENT_DIRECTORY = os.getcwd()

path_to_form_files = None
path_to_form_translation_files = None


def get_form_translations_file_name(form_name, lang):
    return f"{form_name}_translations_{lang}.json"


class DISTRO_FORM:

    def __init__(self, form_name):
        self.form_name = form_name
        self.file_content = None
        self.file_translation = {}

    def get_translation_file_name(self, lang):
        return get_form_translations_file_name(self.form_name, lang)

    def _get_form_path(self):
        return os.path.join(path_to_form_files, f"{self.form_name}.json")

    def _get_form_translations_path(self, lang):
        return os.path.join(
            path_to_form_translation_files,
            self.get_translation_file_name(lang),
        )

    def get_file_content(self):
        if self.file_content is None:
            with open(self._get_form_path(), "r", encoding="utf-8") as file:
                self.file_content = json.load(file)
        return self.file_content

    def get_form_translations_file(self, lang):
        if lang not in self.file_translation:
            try:
                with open(
                    self._get_form_translations_path(lang), "r", encoding="utf-8"
                ) as file:
                    self.file_translation[lang] = json.load(file)
            except FileNotFoundError:
                self.file_translation[lang] = {"translations": {}}
        return self.file_translation[lang]

    def get_text_translations(self, lang):
        return self.get_form_translations_file(lang).get("translations", {})

    def merge_new_translations(self, new_translations, lang):
        current_translations = self.get_text_translations(lang)
        merged_translations = {}

        for key in new_translations.keys():
            if (
                new_translations[key] is None
                and key in current_translations
                and current_translations[key]
            ):
                print(
                    f"Translation for key '{key}' is empty in new translations. Keeping the old translation."
                )
                merged_translations[key] = current_translations[key]
            else:
                merged_translations[key] = new_translations[key]

        return dict(sorted(merged_translations.items()))

    def update_form(self, updated_form_content):
        updated_file_content = self.get_file_content()
        updated_file_content["pages"] = updated_form_content
        self._update_form_file(updated_file_content)

    def _update_form_file(self, form_content):
        with open(self._get_form_path(), "w", encoding="utf-8") as file:
            file.write(json.dumps(form_content, indent=2, ensure_ascii=False))

    def update_translations(self, translations, lang):
        merged_translations = self.merge_new_translations(translations, lang)
        translations_file_content = self.get_form_translations_file(lang)
        translations_file_content["translations"] = merged_translations
        self.update_translations_file(translations_file_content, lang)

    def update_translations_file(self, file_content, lang):
        with open(
            self._get_form_translations_path(lang), "w", encoding="utf-8"
        ) as file:
            file.write(json.dumps(file_content, indent=2, ensure_ascii=False))


class Generated_Form:
    def __init__(self, form_name):
        self.form_name = form_name
        self._file_content = None
        self._file_translation = {}

    def _get_translation_file_name(self, lang):
        return get_form_translations_file_name(self.form_name, lang)

    def _get_file_path(self):
        return os.path.join(
            CURRENT_DIRECTORY, GENERATED_FORM_PATH, f"{self.form_name}.json"
        )

    def _get_file_translation_path(self, lang):
        return os.path.join(
            CURRENT_DIRECTORY,
            GENERATED_FORM_PATH,
            self._get_translation_file_name(lang),
        )

    def get_file_content(self):
        if self._file_content is None:
            with open(self._get_file_path(), "r", encoding="utf-8") as file:
                self._file_content = json.load(file)
        return self._file_content

    def get_form_content(self):
        return self.get_file_content().get("pages", [])

    def get_file_translation_content(self, lang):
        if lang not in self._file_translation:
            try:
                with open(
                    self._get_file_translation_path(lang), "r", encoding="utf-8"
                ) as file:
                    self._file_translation[lang] = json.load(file)
            except FileNotFoundError:
                self._file_translation[lang] = {"translations": {}}
        return self._file_translation[lang]

    def get_text_translations(self, lang):
        return self.get_file_translation_content(lang).get("translations", {})


if __name__ == "__main__":
    path_to_form_files = os.getenv(PATH_TO_FORM_FILES)
    path_to_form_translation_files = os.getenv(PATH_TO_TRANSLATION_FILES)
    if not path_to_form_files:
        print("Environment variable 'PATH_TO_FORM_FILES' not set.")
    elif not path_to_form_translation_files:
        print("Environment variable 'PATH_TO_FORM_FILES' not set.")
    else:
        all_forms = os.getenv(SHEETS_TO_PREVIEW).split(",")

        for name in all_forms:
            form_name = f"{name.replace(" ", "_")}"
            distro_form = DISTRO_FORM(form_name)

            generated_form = Generated_Form(form_name)

            generated_form_content = generated_form.get_form_content()
            distro_form.update_form(generated_form_content)

            for lang in ["ar", "en"]:
                generated_text_translations = generated_form.get_text_translations(lang)
                distro_form.update_translations(generated_text_translations, lang)

            print("Translations updated for form: ", name)
