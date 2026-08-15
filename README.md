# Anonymous reproducibility package

This repository contains the anonymized code, preserved outputs, benchmark
artifacts, and analysis records associated with a manuscript under double-blind
review.

Start with [README_ANONYMOUS_PACKAGE.md](README_ANONYMOUS_PACKAGE.md) for the
scope of the deposit and [README_REPRODUCE.md](README_REPRODUCE.md) for the
analysis commands and expected results.

For a clean Python environment, install the analysis dependencies with:

```bash
python -m pip install -r requirements.txt
```

The dependency file records compatible minimum versions rather than the exact
historical provider environment. The supplied analyses operate on preserved
outputs and do not require API access.

The package supports reproduction of the reported analyses from preserved
outputs. It does not promise byte-identical regeneration of provider responses,
because provider-side randomness and unavailable seeds remain outside the
archive.

No API keys or account credentials are included. Users who run provider-backed
scripts must supply their own credentials through the documented environment or
configuration mechanism.
