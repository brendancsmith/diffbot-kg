# Contributing to Diffbot Knowledge Graph Client

First off, thanks for taking the time to contribute!

The following is a set of guidelines for contributing to `diffbot-kg`, which is hosted on GitHub. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for `diffbot-kg`. Following these guidelines helps the maintainer and the community understand your report, reproduce the behavior, and find related reports.

- **Use a clear and descriptive title** for the issue to identify the problem.
- **Provide a step-by-step description** of the suggested enhancement in as many details as possible.
- **Provide specific examples to demonstrate the steps**. Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those examples.
- **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
- **Explain which behavior you expected to see instead and why.**
- **Include screenshots and/or animated GIFs** which help demonstrate the steps or point out the part of Indeed Job Scraper which the suggestion is related to.

### Development Setup

#### Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) hooks to automatically check code quality before commits. The configuration is compatible with [Trunk.io](https://trunk.io/).

To set up pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

The hooks will automatically run on every commit. You can also run them manually:

```bash
# Run on all files
pre-commit run --all-files

# Run on specific files
pre-commit run --files src/diffbot_kg/models.py
```

The pre-commit configuration includes:
- **Ruff**: Python linting and formatting
- **Prettier**: YAML, JSON, and Markdown formatting
- **yamllint**: YAML linting
- **markdownlint**: Markdown linting
- **Bandit**: Python security checks
- Standard checks: trailing whitespace, file endings, merge conflicts, etc.

### Pull Requests

Please follow these steps to have your contribution considered by the maintainer:

- Set up pre-commit hooks (see Development Setup above) to ensure code quality.
- After you submit your pull request, verify that all status checks are passing.
- While the maintainer reviews your PR, you can also ask for specific people to review your changes.
- Once your pull request is created, it will be reviewed by the maintainer of the project. You may be asked to make changes to your pull request. There's always a chance your pull request won't be accepted.

### Python Styleguide

- All Python must adhere to [PEP 8][PEP8].
- Use type annotations according to [PEP 484][PEP484] and [PEP 526][PEP526].
- Format and lint your python code with [Ruff](https://github.com/jendrikseipp/ruff).
- Include docstrings and comments where appropriate.
- Write tests for new features and bug fixes.

## Attribution

This Contributing guide is adapted from the [Contributing to Atom](https://github.com/atom/atom/blob/master/CONTRIBUTING.md) guide.

[PEP8]: https://www.python.org/dev/peps/pep-0008/
[PEP484]: https://www.python.org/dev/peps/pep-0484/
[PEP526]: https://www.python.org/dev/peps/pep-0526/
