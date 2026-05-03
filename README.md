# GARI

GARI (GenAI Assessment Risk Index) is a Streamlit web app that helps educators estimate how vulnerable an assessment design may be to inappropriate or unintended generative AI use.

It is designed as a decision-support tool for reflection and redesign, not as a standalone compliance or disciplinary system.

## Live App

This project is intended for deployment on Streamlit Community Cloud.

- Production URL: TBA

## What GARI Does

GARI scores assessments across four dimensions:

- Type
- Delivery
- Authenticity
- Guidance

The score is then adjusted by assessment weighting (0-100%) and mapped to a risk category:

- Insignificant
- Minor
- Moderate
- High
- Critical

## Key Features

- Multi-page Streamlit interface (Home, Risk Calculator, FAQs, Contact)
- Single assessment mode with instant scoring
- Batch mode for CSV uploads and multi-row scoring
- Validation feedback for invalid batch rows
- Downloadable outputs:
	- Scored CSV (batch)
	- PDF report (single and batch summaries)
- Optional high-risk mitigation tips for redesign discussions

## App Pages

- Home: overview of scoring dimensions and how to use the calculator
- Risk Calculator:
	- Single mode: interactively score one assessment
	- Batch mode: upload CSV, view summaries/charts, export scored data
- FAQs: common usage and interpretation questions
- Contact: send messages to the project team when SMTP is configured

## Run Locally

### 1. Create and activate a conda environment

On Windows (PowerShell):

```powershell
conda create -n gari python=3.11 -y
conda activate gari
```

### 2. Install dependencies

```bash
pip install -r streamlit_app/requirements.txt
```

### 3. Start the app

```bash
streamlit run streamlit_app/Home.py
```

## Batch CSV Requirements

Required columns:

- type
- delivery
- authenticity
- guidance
- weighting

Accepted weighting range is 0 to 100.

Additional columns are allowed and are preserved in the scored CSV output.

## Project Structure

```text
streamlit_app/
	Home.py
	core.py
	requirements.txt
	assets/
	pages/
```

## Disclaimer

GARI supports educator judgement. Results should be interpreted alongside institutional policy, subject context, and professional expertise.

## License

This project is licensed under the terms of the LICENSE file in this repository.
