# Change Log

## 0.6.0

- Default ``host`` configuration option to ``circleci.com``. This way it works out of the
  box for public / SaaS Circle CI installations.

- Add new ``run_project_build`` action which allows user to trigger a build for all the
  workflows for a particular project which utilizes workflows version v2.0.

## 0.5.3

- Ignore payloads with no content (Trigger won't be posted)

## 0.5.2

- Minor linting fixes

## 0.5.0

- Updated action `runner_type` from `run-python` to `python-script`
