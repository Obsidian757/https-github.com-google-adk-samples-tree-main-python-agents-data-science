# n8n Workflows — 12th House AI

Import these JSON files into your n8n instance at `http://your-vps:5678`.

## Workflows

| # | Workflow | Trigger | File |
|---|----------|---------|------|
| 1 | **License Sync** | Daily cron | `01_license_sync.json` |
| 2 | **Deadline Monitor** | Weekly cron | `02_deadline_monitor.json` |
| 3 | **Budget Alert** | Daily cron | `03_budget_alert.json` |
| 4 | **Client Onboarding** | Webhook (landing page form) | `04_client_onboarding.json` |
| 5 | **Monthly Report** | Monthly cron + on-demand webhook | `05_compliance_report.json` |

## Setup

1. Open n8n UI → **Workflows** → **Import from File**
2. Import each JSON file
3. Configure credentials:
   - **OpenAI Admin API Key** (for license sync)
   - **Microsoft Graph OAuth2** (for O365 license data)
   - **SMTP** (for email alerts)
   - **Slack Webhook** (optional, for Slack alerts)
4. Set environment variables in `docker-compose.yml` or n8n settings
5. Activate each workflow

## Webhook Endpoints

Once deployed, these URLs are available:

- `POST http://your-vps/webhook/onboard-client` — Client onboarding form
- `POST http://your-vps/webhook/generate-report` — Trigger report on demand
