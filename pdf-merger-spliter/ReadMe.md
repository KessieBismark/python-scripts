# PDF Merger and Splitter

Merge several PDF files into one, or split a PDF into one file per page.

## Requirements

```bash
python3 -m pip install pypdf
```

The older `PyPDF2` is used automatically if `pypdf` isn't installed.

## Usage

Merge, in the order the files are given:

```bash
python3 main.py merge first.pdf second.pdf third.pdf
```

That writes `first_merged.pdf` next to the first input. To choose the name, and
to overwrite a file that is already there:

```bash
python3 main.py merge first.pdf second.pdf -o combined.pdf --force
```

Split a PDF into single pages (`report_page_1.pdf`, `report_page_2.pdf`, ...):

```bash
python3 main.py split report.pdf
```

Write those pages somewhere else:

```bash
python3 main.py split report.pdf -d pages/
```

## Use from Python

```python
from main import merge_pdfs, split_pdf

merge_pdfs(["a.pdf", "b.pdf"], "out.pdf")
split_pdf("out.pdf", outdir="pages")       # outdir is optional
```

## Notes

- Mixed page sizes are kept as they are; a merged file can hold both A4 and
  Letter pages.
- PDFs locked with a real password are reported as an error rather than skipped.
- Merging refuses to overwrite an existing output unless `--force` is passed,
  and refuses to write over one of its own inputs.
