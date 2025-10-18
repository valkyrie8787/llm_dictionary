```
 ██████╗ ██████╗ ███████╗███╗   ██╗███╗   ██╗██╗   ██╗██████╗ ██╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║████╗  ██║██║   ██║██╔══██╗██║
██║   ██║██████╔╝█████╗  ██╔██╗ ██║██╔██╗ ██║██║   ██║██████╔╝██║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██║╚██╗██║██║   ██║██╔══██╗██║
╚██████╔╝██║     ███████╗██║ ╚████║██║ ╚████║╚██████╔╝██║  ██║██║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝
```

```
███████╗██╗  ██╗██╗      █████╗ ██████╗ 
██╔════╝╚██╗██╔╝██║     ██╔══██╗██╔══██╗
█████╗   ╚███╔╝ ██║     ███████║██████╔╝
██╔══╝   ██╔██╗ ██║     ██╔══██║██╔══██╗
███████╗██╔╝ ██╗███████╗██║  ██║██████╔╝
╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ 
```

# OpenNuri Dictionary Project

*"Building a high-quality, multilingual lexical database aligned by semantic meaning, licensed under MIT for unrestricted use."*

OpenNuri is an ambitious open-source initiative to construct a comprehensive, sense-aligned multilingual dictionary database. Leveraging WordNet's semantic structure as its backbone, this project aims to provide a freely accessible, high-quality lexical resource for developers, researchers, and linguists. Our core mission is to overcome the limitations of existing resources by ensuring data quality through a robust validation pipeline, maintaining a permissive MIT license, and building a sustainable, community-driven ecosystem.

-----

## 🏛️ Grand Blueprint: Core Principles & Vision

Our development is guided by a set of core principles designed to ensure the project's long-term success and utility.

  * **MIT License First:** The entire project, including the core database, is maintained under the MIT license. Components with non-compatible licenses (e.g., CC-BY-SA from certain WordNets) are strictly isolated and managed under a clear policy outlined in our `LICENSE_POLICY.md`.
  * **Semantic Alignment:** All lexical data is aligned based on the semantic 'Sense' defined in Princeton WordNet, enabling precise cross-lingual comparisons and applications.
  * **Quality & Transparency:** Data quality is not an afterthought. We employ a multi-layered validation process, including automated schema checks, custom linguistic validators, and quantitative metrics (BLEU, confidence scores). All data points are tagged with `Provenance` and a `confidence_score` to ensure full transparency.
  * **Community-Driven & Sustainable:** We are building a virtuous cycle where community contributions (e.g., validating "Gold" samples, suggesting new examples) directly feed into model fine-tuning (QLoRA), continuously improving the database for everyone.

-----

## 🏗️ Project Architecture & Pipeline

The project is built on a modular, robust data generation pipeline designed for scalability and maintainability.

  * **File Structure:**

    ```
    llm_dictionary/
    ├── 🏗️ builder.py             # Main script to run the entire data generation pipeline
    ├── 🏛️ schemas/               # Defines the core data structures (Pydantic models)
    ├── 🗣️ lang_plugins/          # Parsers for 8 source languages (EN, DE, KO, HR, etc.)
    ├── ⚖️ validators/            # Data quality and schema validation logic
    ├── 🛠️ utils/                 # Shared utilities (quality scoring, BLEU, etc.)
    ├── 📚 offline_resources/     # Raw source data (WordNet, OMW)
    ├── 📜 LICENSE
    ├── 📜 LICENSE_POLICY.md      # Detailed license policy for all data components
    └── 🐍 requirements.txt       # Required Python libraries
    ```

  * **Data Generation Workflow:** The `builder.py` script orchestrates a multi-stage pipeline:

    1.  **Parsing (`lang_plugins`):** Raw data from sources like WordNet and the Open Multilingual Wordnet (OMW) is parsed and structured.
    2.  **LLM Augmentation:** A powerful Mixture of Experts (MoE) model (gpt-oss-120b) is used to enrich the data, generating translations, inflections, and example sentences.
    3.  **Validation (`validators`):** The generated data undergoes rigorous validation. This includes:
          * `schema_validator`: Ensures structural integrity against our Pydantic models.
          * `custom_validator`: Applies language-specific logical and semantic rules.
    4.  **Quality Scoring (`utils/quality_scorer.py`):** An automated quality score is calculated for each entry using metrics like back-translation BLEU scores and embedding similarity.
    5.  **Output:** The final, validated data is produced in user-friendly formats (JSONL, Parquet).

-----

## 🚀 Getting Started & Contributing

We welcome contributions from developers, linguists, and language enthusiasts. Your expertise can help us improve the quality and coverage of this valuable resource.

  * **Installation:**
    ```bash
    git clone https://github.com/[your_username]/llm_dictionary.git
    cd llm_dictionary
    pip install -r requirements.txt
    ```
  * **How to Contribute:**
    1.  **Data Validation:** Help us review and validate "Gold" sample data.
    2.  **Improve Language Parsers:** Enhance the parsing logic for your language of expertise.
    3.  **Suggest New Examples:** Propose high-quality example sentences for different word senses.
    <!-- end list -->
      * Please read our **`CONTRIBUTING.md`** guide for detailed instructions on how to get involved.

-----

## 🗺️ Project Roadmap (v1.4)

Our development is structured in clear, iterative phases.

  * **Phase 1: Foundation & Core Schema (Complete):** Established the final Sense-centric data schema, validator logic, and a clear license policy.
  * **Phase 2: Core Pipeline Development (In Progress):** Building the modular data generation pipeline (`builder.py`) and implementing the hybrid quality scoring system.
  * **Phase 3: Data Generation & Refinement:**
      * **Pilot Run:** Generate and manually review a 1,000-entry pilot dataset to refine the validation rules.
      * **v0.1 'Silver' Dataset:** Execute the full pipeline to generate the first large-scale, version-controlled dataset.
  * **Phase 4: Iteration, Community & Deployment:**
      * **Public Release:** Publish the initial dataset on platforms like Hugging Face Datasets.
      * **Fine-Tuning Loop:** Implement a CI/CD workflow using GitHub Actions to fine-tune our models based on community feedback and contributions.

-----

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE` file for full details. For information on the licenses of individual data components included in this project, please see our `LICENSE_POLICY.md`.
