# Sysdig Compliance Report Generator

This project creates a "glossy" style summary report for current compliance
findings in the Sysdig Secure console. The detaisl in the report reflect
the data in the Sysdig Console at the time of execution. The intention of
this report is to give an overview for the current standing of a given policy
and its related requirements.

The report generated will be bound by compliance "zone" in order for the
returned info to have usable context. More than one policy per zone can be
included in the report.

## Prerequisites

This project is written in Python and requires Python 3 to execute.

This project requires **[wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)** for PDF generation. We are not using any
features that would require a "patched" version.

Other requirements are captures in the `requirements.txt` generated from `pip`.

## Usage

```$ python ./report_generator.py```

```
Usage: report_generator.py [options]

Options:
  -h, --help            show this help message and exit
  -z ZONE, --zone=ZONE  limit report results to a specific zone
  -p POLICY, --policy=POLICY
                        specific policy, or list of policies to create report
                        for - if more than one policy, use the format "<policy
                        name1>, <policy name2>, ..."
  -s SECURE_URL, --secure-url=SECURE_URL
                        Sysdig Secure Console base URL
  -t TOKEN, --token=TOKEN
                        Sysdig Secure API Token
  -l LOGGING, --logging=LOGGING
                        Set logging level for report generator
```

The following options can also be provided via environment variable:

| Option | ENV Var |
|--------|---------|
| --secure_url | SDC_SECURE_URL |
| --token | SDC_SECURE_TOKEN |


## Output

Reports will be written to the ```reports``` directory under the project root dir.
Reports will be named releative to the time they were generated.
