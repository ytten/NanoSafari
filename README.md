# NanoSafari

This repository contains the code for **NanoSafari**.

## Grouped Iterative Validation and Information Extraction (GIVE) Framework

To use the GIVE framework, please specify your configuration in the `config.yaml` file. Papers are preprocessed using **Grobid** and **S2ORC-pdf2json** tools, which output structured data into CSV files for subsequent processing.

Once the configuration is set up, execute the following command to start the extraction:

```bash
python run.py
```