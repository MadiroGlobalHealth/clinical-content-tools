![](https://github.com/Madiro-org/clinical-content-tools/actions/workflows/pylint.yml/badge.svg)

# Clinical Content Management Tools

This repository aims to provide a set of scripts and utilities to (hopefully) facilitate the management of clinical content using [OpenConceptLab (OCL)](https://openconceptlab.org/) and [OpenMRS 3 Forms](https://o3-docs.openmrs.org/docs/forms-in-o3/build-forms-with-o3-form-builder.en-US). The tools are designed to automate repetitive tasks across various implementers, facilities, and forms.

The vision behind this set of tools is to evolve into a user-friendly and **flexible toolkit** covering critical and often cumbersome stages of Health Metadata Management. Here is an **overview and progress** made on each stage:

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#f0f3f7',
      'primaryTextColor': '#000',
      'primaryBorderColor': '#f0f3f7',
      'lineColor': '#000',
      'secondaryColor': '#000',
      'tertiaryColor': '#000'
    }
  }
}%%
flowchart LR
    A["<div style='width:250px; height:250px; display:flex; flex-direction:column; justify-content:center; text-align:center;'>
         <div style='font-size:22px;'><b>🏗️<br><br>Paper-To-Form Converter</b></div>
         <div><br>1st tests made, prompting refined</div>
         <div>Target release: June 2025</div>
         </div>"] -->
    B["<div style='width:250px; height:250px; display:flex; flex-direction:column; justify-content:center; text-align:center;'>
         <div style='font-size:22px;'><b>🏗️<br><br>Concept standardization and mapping</b></div>
         <div><br>OCL Mapper v2 in progress</div>
         <div>Target release: June 2025</div>
         </div>"]
    B -->
    C["<div style='width:250px; height:250px; display:flex; flex-direction:column; justify-content:center; text-align:center;'>
         <div style='font-size:22px;'><b>🗓️<br><br>Content creation assistant for OCL</b></div>
         <div><br>Planned</div>
         </div>"]
    C -->
    D["<div style='width:250px; height:250px; display:flex; flex-direction:column; justify-content:center; text-align:center;'>
         <div style='font-size:22px;'><b>🏗️<br><br>Metadata validation assistant</b></div>
         <div><br>Initial tool being prepared</div>
         </div>"]
    D -->
    E["<div style='width:250px; height:250px; display:flex; flex-direction:column; justify-content:center; text-align:center;'>
         <div style='font-size:22px;'><b>🚀<br><br>Metadata to OpenMRS 3 form generation</b></div>
         <div><br>Used with MSF forms</div>
         <div>Automation coverage: 80%</div>
         </div>"]
    E -->
    F["<div style='width:250px; height:250px; display:flex; flex-direction:column; justify-content:center; text-align:center;'>
         <div style='font-size:22px;'><b>🏗️<br><br>Metadata to e2e test cases automation</b></div>
         <div><br>1st tests made, prompting refined</div>
         <div>Target release: June 2025</div>
         </div>"]

```

### Below if an introduction video about the standardization and mapping tooling - Though deprecated and now replaced by OCL Mapper.

[Here is an explanation/demo video](https://www.youtube.com/watch?v=s9S4FaZib1U)

<a href="https://www.loom.com/share/d2d049a21a7347d6a9af951e2e5c0ba9?sid=5bcbc54f-e0e3-4ad7-a039-8ced49af9813" target="_blank">
  <img height="400" alt="Screenshot 2024-07-17 at 11 17 13 PM" src="https://github.com/user-attachments/assets/8b53ec7b-15e8-4eec-b769-83905f8ba40c">
</a>

## Python scripts

1. **OCL concept automatching**: `matcher.py` automates the process of matching OCL concepts.
2. **XLSX to O3 form schema conversion**: `converter.py` converts XLSX files to O3 (OpenMRS 3) form JSON schemas.

## Tooling scripts

3. **OCL Source fetcher**: `fetcher.py` download a local snapshot of an OCL source for the automatch.
4. **Source Filter**: `filter.py` creates a filtered version of the source snapshot to improve performance.
5. **Updating the form and translations in your EMR repo**: `update_form_and_translations.py` takes the newly generated form and translation files and updates them in your repo almost instantly.

## Requirements

To run these scripts, you will need the following:

- Python 3.x
- Pandas library
- Openpyxl library

You can also run install the required dependencies using: `pip install -r requirements.txt`

## Installation

To get started with the Clinical Content Management Tools, follow these steps:

1. Clone the repository: `git clone https://github.com/michaelbontyes/clinical-content-tools.git`
2. Navigate to the project directory: `cd clinical-content-tools`
3. Install Python 3.x (if not already installed):
   - For Windows: Download and install Python from the official website: https://www.python.org/downloads/
   - For macOS: Install Python using Homebrew: `brew install python3`
   - For Linux: Use the package manager of your distribution (e.g., `apt-get install python3` for Ubuntu)
4. Install pip (if not already installed):
   - For Windows: pip is usually included with Python installation. If not, download get-pip.py from https://bootstrap.pypa.io/get-pip.py and run `python get-pip.py`
   - For macOS and Linux: Use the package manager of your distribution (e.g., `apt-get install python3-pip` for Ubuntu)
5. Install the required dependencies: `pip install -r requirements.txt`

## Getting started

Create a `.env` file from the provided `.env.example` file and update in the required environment variables. You could also use the default values provided in the `.env.example` file for testing purposes.

```bash
cp .env.example .env
```

This file contains the common configuration variables. You can modify the values as needed.

### Common configuration file

- `sheets`: A list of sheet names in the metadata Excel file that contain the concepts to be matched.
- `OCL_URL`: The base URL of the OCL server where the concepts will be matched.
- `FUZZY_THRESHOLD`: The fuzzy string matching threshold (default is 95). This value determines the minimum similarity score required for a match.
- `METADATA_FILEPATH`: The file path of the metadata Excel file containing the concepts to be matched.
- `OUTPUT_DIR`: The directory where the generated form schemas will be saved.
- `automatch_references`: A dictionary containing the details of the OCL sources to be used for matching. Each key in the dictionary represents a source name, and the corresponding value is another dictionary containing the source details.

### Usage and configuration for `matcher.py`

The `matcher.py` script is designed to automate the process of matching OCL concepts based on the provided configuration settings. Below is a detailed explanation of the configuration parameters and their usage.

To use the `matcher.py` script, you need to provide two input files:

1. An Excel file containing the data to be matched. Example provided: `metadata_example.xlsx`
2. JSON files containing the reference data for matching. Examples provided in `ocl_source_snapshots`: `MSF_Source_Filtered_20240712_163433.json` for MSF Source and `CIEL_Source_Filtered_20240708_153712.json` for CIEL Source

You can configure the destination columns where to write the suggested matches, for each OCL source provided:

- `source_filepath`: The file path of the JSON file containing the concepts from the OCL source.
- `suggestion_column`: The name of the column in the metadata Excel file that contains the suggestions for matching concepts.
- `external_id_column`: The name of the column in the metadata Excel file that contains the external IDs of the concepts.
- `description_column`: The name of the column in the metadata Excel file that contains the descriptions of the concepts.
- `datatype_column`: The name of the column in the metadata Excel file that contains the datatypes of the concepts.
- `dataclass_column`: The name of the column in the metadata Excel file that contains the classes of the concepts.
- `score_column`: The name of the column in the metadata Excel file that contains the scores of the matching concepts.

To use the `matcher.py` script with the provided configuration and metadata Xlsx file, simply run the script from the command line:

```bash
python matcher.py
```

The script will read the configuration from the `config.json` file, process the concepts, and generate the form schemas based on the matching results.

### Usage and configuration for `converter.py`

Similarly to `matcher.py`, use the `converter.py` script with the provided in the Excel file containing the form configuration metadata.

To run the script, use the following command:

```bash
python converter.py
```

The script will then generate OpenMRS 3 form configurations and translation files from the data in the Excel file, and store them in the folder `generated_form_schemas`. Then you can copy-paste them directly into OpenMRS Initializer folder or Form Builder UI.

### Usage and configuration for `update_form_and_translations.py`

This script is designed to be executed after `converter.py`. It updates the form and translation files in the `distro` repo using the newly generated files from the `generated_form_schemas/` folder. The script relies on properties defined in the `.env` file to locate the distro repository and its relevant directories.

You can configure the following properties in the `.env` file:

- `PATH_TO_FORM_FILES`: The absolute path to the `ampathforms/` folder where the form JSON files are stored. Use the `pwd` command in your `ampathforms/` directory to get the exact path.
- `PATH_TO_TRANSLATION_FILES`: The absolute path to the `ampathformtranslation/` folder where the translation files are stored. Use the `pwd` command in your `ampathformtranslations/` directory to get the exact path.

> **Note:** The form and translation files must already exist in the distro repository. If they do not, you can manually copy the generated files into the appropriate directories. This script is intended to **update** existing files, minimizing manual copy-paste operations for developers or users.

To execute the script, use the following command:

```bash
python update_form_and_translations.py
```

You can chain the execution of `converter.py` and `update_form_and_translations.py` as follows:

```bash
python converter.py && python update_form_and_translations.py
```

This will:

1. Generate the form and translation files using `converter.py`.
2. Update the `pages` property in the form JSON files and the `translations` in the respective translation files within your distro repository.

## Contributing

Contributions to the Clinical Content Management Tools project are welcome! If you have any suggestions, improvements, or bug fixes, please feel free to open an issue or submit a pull request.

## Acknowledgments

The Clinical Content Management Tools project is made possible thanks to [OpenConceptLab](https://openconceptlab.org/) and [OpenMRS](https://openmrs.org/) communities. Special thanks to the contributors who have contributed to the development of these tools.

<div>
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/OpenMRS_logo_2008.svg/1280px-OpenMRS_logo_2008.svg.png" height=60px>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://pbs.twimg.com/profile_images/1699787210458038272/dvtN516-_400x400.png" height=60px>
</div>

## Contact

For any questions, please contact [Michael Bontyes](https://github.com/michaelbontyes) or reach out to the OpenConceptLab Squad and OpenMRS community.

<div>
<img src="https://www.msf.org/themes/custom/msf_theme/ogimage.jpg" height=60px>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://github.com/MSF-OCG/LIME-EMR-project-demo/raw/main/docs/_media/Madiro.png" height=60px>
</div>

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
