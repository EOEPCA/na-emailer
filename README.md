# na-emailer

__WARNING__: This README.md is a work in progress and may contain outdated information.


Knative function that receives **CloudEvents**, optionally filters them (typically via configuration injected by a **Knative SinkBinding**), renders **Jinja2** templates (subject + plain/html), and sends an email notification.

## How it works
- Accepts an incoming HTTP request carrying a CloudEvent (binary or structured).
- Loads configuration from environment variables (all `NA_*`).
- Applies attribute filters (e.g. `type`, `source`, `subject`, extensions).
- Selects templates based on CloudEvent `type`.
- Sends email using a pluggable client backend (default: `yagmail`).

## Logging
- `NA_LOG_LEVEL`: `DEBUG|INFO|WARNING|ERROR` (default: `INFO`).
- The service logs a startup line **at process start**:
  - `na-emailer started (ready to receive events)`
- For each request it logs: received event, filtered out / rendered / dry-run / send result.

## Environment variables
### Filtering
- `NA_FILTERS_JSON`: JSON object of required matches.
  - Example: `{"type":"com.acme.ready","source":"/sensor"}`
  - Values can be scalars or arrays (array means “actual in expected”).
- `NA_FILTER_MODE`: `all` (default) or `any`.

### Template selection
- `NA_TEMPLATES_DIR`: templates folder.
  - **Local default**: the repo’s `./templates` directory (resolved automatically).
  - **Container default**: `/app/templates` (the Dockerfile copies templates there).
- `NA_TEMPLATE_MAP_JSON`: JSON object mapping CloudEvent type to template base name.
  - Example: `{"com.acme.job.done":"job_done"}`
- `NA_TEMPLATE_DEFAULT`: fallback template base name (default `default`).
- `NA_TEMPLATE_STRICT_UNDEFINED`: `true|false` (default `false`).

### Email
- `NA_EMAIL_CLIENT`: email backend (default `yagmail`).
- `NA_EMAIL_FROM`: optional sender.
- `NA_EMAIL_TO`: comma-separated recipients.
- `NA_EMAIL_CC`, `NA_EMAIL_BCC`: optional.
- `NA_EMAIL_SUBJECT_PREFIX`: optional prefix.
- `NA_DRY_RUN`: `true|false` (if true, renders but doesn’t send).

### Yagmail backend
Required when `NA_EMAIL_CLIENT=yagmail` and `NA_DRY_RUN=false`:
- `NA_YAGMAIL_USER`
- `NA_YAGMAIL_PASSWORD`

Optional:
- `NA_YAGMAIL_HOST`, `NA_YAGMAIL_PORT`
- `NA_YAGMAIL_SMTP_STARTTLS`, `NA_YAGMAIL_SMTP_SSL`

## Templates
Templates are chosen by **base name**.

For base name `default` the renderer will look for:
- `default.subject.j2` (required)
- `default.txt.j2` (optional)
- `default.html.j2` (optional)

The template context includes:
- `ce`: CloudEvent attributes (plus extensions)
- `data`: the CloudEvent data

## Local development
### Option A: run via `start.py` (recommended)
This prints an explicit “Waiting for CloudEvents...” line and defaults to dry-run.

```zsh
python -m pip install -e '.[test]'
python start.py
```

### Option B: run via Functions Framework directly

```zsh
python -m pip install -e '.[test]'
export NA_DRY_RUN=true
functions-framework --target handle --port 8080
```

### Send a test CloudEvent

```zsh
curl -i http://localhost:8080/ \
  -H 'Content-Type: application/cloudevents+json' \
  -d '{"specversion":"1.0","id":"1","source":"/local","type":"com.acme.test","datacontenttype":"application/json","data":{"hello":"world"}}'
```

## Notes
This repo is intentionally small and focused (core runtime + tests).

Add new email backends by implementing `app.clients.base.EmailClient` and wiring it in `app.clients.factory.create_email_client`.
