# NanoSafari

This repository contains the code for **NanoSafari**.

## Grouped Iterative Validation and Information Extraction (GIVE) Framework

To use the GIVE framework, please navigate to the `GIVE` directory and specify your configuration in the `config.yaml` file. Papers are preprocessed using **Grobid** and **S2ORC-pdf2json** tools, which output structured data into CSV files for subsequent processing.

Once the configuration is set up, execute the following command to start the extraction:

```bash
python run.py
```

### Multi-Agent QA Framework

To use the Multi-Agent QA Framework, navigate to the `Multiagent_QA` directory and run:

```bash
python run.py
```

The output will be saved as `output.md` in the same directory.

