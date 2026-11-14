# SentryAI – Agentic Security Testing Toolkit

SentryAI is a Python-based security testing toolkit designed to organize and manage security assessments in an authorized, controlled practice environment.

The project currently focuses on the local **Damn Vulnerable Web Application (DVWA)** environment. It provides modules for configuration validation, security findings management, assessment workflow orchestration, and report generation.

NeuroSploit is the planned scanning framework. Its actual integration is still pending verification.

---

## 1. Project Objectives

- Provide a structured approach to managing security assessments.
- Validate target configuration and testing scope.
- Store and organize security findings.
- Categorize findings based on severity.
- Generate reports in JSON and Markdown formats.
- Provide an interface for future scanner integration.

## 2. Project Scope

| Component | Description |
|---|---|
| Practice target | Local DVWA |
| Planned scanning framework | NeuroSploit |
| Programming language | Python |
| Testing framework | pytest |
| Report formats | JSON and Markdown |
| Execution environment | Local development environment |

**Security restriction:** All security testing is intended for the approved local DVWA practice environment. Testing against external or unauthorized systems is outside the project scope.

## 3. Features Implemented

### Configuration Module
- Validates target URLs and configuration settings.
- Checks the configured testing scope.
- Restricts accepted targets to local host addresses.

### Findings Management
- Provides structured security finding objects.
- Supports Critical, High, Medium, Low, and Informational severity levels.
- Organizes findings using a finding collection.

### Reporting Module
- Generates JSON reports.
- Generates Markdown reports.
- Includes finding details and severity summaries.

### Assessment Workflow
- Connects configuration, scanning interface, findings, and reporting components.
- Tracks assessment status.
- Handles successful and failed workflow execution.

### Result Adapter
- Converts scanner-result JSON data into SentryAI finding objects.
- Validates incoming result data.
- Checks that the reported target matches the configured target.

### NeuroSploit Runner Interface
- Provides an interface intended to connect SentryAI with NeuroSploit.
- Actual execution with the NeuroSploit framework has not yet been verified.

---

## 4. Project Structure

```text
sentryai-toolkit/
│
├── toolkit/
│   ├── config.py
│   ├── neurosploit_runner.py
│   ├── findings.py
│   ├── reporting.py
│   ├── assessment.py
│   └── result_adapter.py
│
├── tests/
│   ├── test_config.py
│   ├── test_neurosploit_runner.py
│   ├── test_findings.py
│   ├── test_reporting.py
│   ├── test_assessment.py
│   ├── test_result_adapter.py
│   └── test_result_adapter_workflow.py
│
├── examples/
│   └── sample_scan_results.json
│
├── reports/
│   ├── sentryai_report.json
│   └── sentryai_report.md
│
├── demo.py
├── requirements-dev.txt
├── .gitignore
└── README.md
```

The `reports/` directory contains generated demonstration output and is excluded from Git tracking.

---

## 5. Development Environment Setup

### Prerequisites

- Python 3.13
- Git
- A Python virtual environment
- Docker Desktop and WSL2 for the local DVWA environment

### Clone the Repository

```powershell
git clone https://github.com/molsyspvtltd/sentryai-toolkit.git

cd sentryai-toolkit
```

### Create a Virtual Environment

```powershell
python -m venv .venv
```

### Activate the Environment

```powershell
.venv\Scripts\Activate.ps1
```

### Install Development Dependencies

```powershell
python -m pip install -r requirements-dev.txt
```

---

## 6. Running Automated Tests

Run the automated test suite using:

```powershell
python -m pytest -q
```

**Latest confirmed test result: 35 passed.**

The tests cover:

- Configuration validation
- Findings management
- Report generation
- Assessment workflow
- Runner interface behaviour
- Result adapter validation
- Workflow integration

The runner tests use mocked subprocess behaviour. Passing these tests does not establish that NeuroSploit has been installed or executed successfully.

---

## 7. Running the Offline Demonstration

Run:

```powershell
python demo.py
```

The demonstration:

1. Loads synthetic sample scan-result data.
2. Validates and converts the sample results.
3. Processes the findings through the assessment workflow.
4. Generates JSON and Markdown reports.
5. Displays the assessment status and severity summary.

### Expected Demonstration Result

The latest confirmed demonstration produced:

- Assessment status: Completed
- Total sample findings: 2
- Medium findings: 1
- Informational findings: 1
- JSON report generated successfully
- Markdown report generated successfully

### Generated Reports

```text
reports/
├── sentryai_report.json
└── sentryai_report.md
```

**Important:** The demonstration uses synthetic sample data. It does not perform a live security scan or establish that the sample findings are actual vulnerabilities.

---

## 8. Current Integration Status

| Component | Status |
|---|---|
| Configuration module | Implemented |
| Findings management | Implemented |
| Reporting module | Implemented |
| Assessment workflow | Implemented |
| Result adapter | Implemented |
| NeuroSploit runner interface | Implemented; actual integration unverified |
| Local DVWA setup | Completed |
| Offline demonstration | Working |
| Automated tests | 35 passed in latest confirmed run |
| End-to-end scanner testing | Pending |

---

## 9. Pending Work and Future Improvements

1. Confirm the expected NeuroSploit installation and integration approach.
2. Verify the runner interface with the approved scanner environment.
3. Connect actual scanner output to the SentryAI result adapter.
4. Complete end-to-end verification in the local DVWA environment.
5. Improve documentation based on integration results.
6. Complete final repository integration and review.

---

## 10. Project Safety and Limitations

- The project is restricted to authorized local practice testing.
- The current offline demonstration uses synthetic data.
- No live NeuroSploit scan has been completed or verified.
- The runner interface and its mocked tests should not be considered proof of actual scanner integration.
- Actual scanner integration and end-to-end verification remain pending.

---

## 11. Project Status

The core SentryAI modules have been implemented, and the latest confirmed automated test run passed all 35 tests.

The offline demonstration successfully processes synthetic findings and generates JSON and Markdown reports.

The primary remaining objective is to verify the NeuroSploit integration and complete end-to-end testing within the approved local DVWA environment.

### NeuroSploit Integration

- Successfully installed and verified NeuroSploit CLI version 4.4.0.
- Integrated a safe CLI verification interface into SentryAI.
- Successfully retrieved the NeuroSploit agent inventory through the CLI.
- Verified that the configured local DVWA target is accepted by SentryAI's scope validation.
- Actual scanner-result import from a completed DVWA assessment is still pending.

### Current Integration Status

| Component | Status |
|---|---|
| Configuration module | Implemented |
| Findings management | Implemented |
| Reporting module | Implemented |
| Assessment workflow | Implemented |
| Result adapter | Implemented |
| NeuroSploit CLI verification | Verified |
| NeuroSploit version check | Successful |
| NeuroSploit agent inventory | Retrieved successfully |
| Local DVWA setup | Completed |
| Offline demonstration | Working |
| Automated tests | 35 passed |
| Actual DVWA assessment | Pending |
| End-to-end scanner-result validation | Pending |

### Verification Results

The following checks have been completed:

- NeuroSploit CLI version: 4.4.0
- Agent inventory retrieved: 485 agents reported
- Local DVWA target configuration: Accepted
- Automated test suite: 35 passed, 0 failed
- Offline demonstration: Successfully generated JSON and Markdown reports.

### Limitations

- The offline demonstration uses synthetic sample findings.
- The NeuroSploit CLI verification checks installation and agent availability; it does not perform a security assessment.
- No actual DVWA vulnerabilities have been confirmed through a completed NeuroSploit assessment.
- End-to-end scanner-result validation remains pending.

### Project Status

The core SentryAI modules have been implemented and tested. NeuroSploit has been installed, and its CLI communication and agent inventory retrieval have been verified.

The result adapter and reporting workflow are ready to process structured scanner results. The remaining milestone is to validate actual scanner output and complete an approved, supervised end-to-end assessment in the local DVWA environment.


### Current Verification Status

- Automated test suite: **39 tests passed**.
- NeuroSploit CLI version check: **4.4.0 verified**.
- NeuroSploit agent inventory: **485 agents reported**.
- Executable discovery through `NEUROSPLOIT_PATH`: verified.
- SentryAI demonstration: successfully generates JSON and Markdown reports using synthetic sample findings.
- No live security scan has been performed.
- Mentor-approved DVWA assessment and validation of actual scanner findings remain pending.

**Important:** Successful CLI verification confirms that NeuroSploit is installed and accessible. It does not confirm completion of an end-to-end security assessment.