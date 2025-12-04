# GitHub Actions Workflows

## Keep Streamlit App Alive

**Purpose**: Prevent Streamlit Community Cloud from hibernating the app due to inactivity.

**File**: `keepalive.yml`

### How It Works

Streamlit Community Cloud hibernates apps after 12 hours of no traffic. This workflow makes periodic HTTP requests to keep the app active during business hours.

### Schedule

- **Frequency**: Every hour
- **Time**: 7am-10pm PST (daily)
- **UTC Conversion**: 
  - 7am PST = 15:00 UTC
  - 10pm PST = 06:00 UTC (next day)
  - Spans two cron schedules to cover the full range

### Security Design

**Reviewed by Oracle** - This approach follows security best practices:

- ✅ **No authentication needed** - treats keep-alive as normal public traffic
- ✅ **Public URL only** - no secrets or special endpoints
- ✅ **Minimal permissions** - workflow has no GitHub permissions
- ✅ **Read-only operation** - GET request with no side effects
- ✅ **Custom User-Agent** - `streamlit-keepalive-bot` for log filtering
- ✅ **Query parameter** - `?healthcheck=1` for monitoring
- ✅ **Fail-safe design** - `|| true` prevents workflow failures from blocking other jobs

### Monitoring

**App Logs** (Streamlit Cloud):
```
Healthcheck ping received from keep-alive bot
```

**GitHub Actions Logs**:
```
Keep-alive ping completed at 2025-12-03 15:00:00 UTC
```

**Verification**:
1. Go to "Actions" tab in GitHub
2. Select "Keep Streamlit App Alive" workflow
3. Check recent runs for success status
4. View logs for timestamps and curl output

### Manual Triggering

For testing or one-off pings:

1. Go to GitHub → Actions tab
2. Click "Keep Streamlit App Alive" workflow
3. Click "Run workflow" button
4. Select branch and confirm

### Configuration

**URL**: `https://creative-direction-decks.streamlit.app/`  
**Timeout**: 10 seconds max  
**Retry logic**: None (fail-safe with `|| true`)

### Troubleshooting

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| Workflow failing | Check Actions logs for curl errors | Verify app URL is accessible |
| App still hibernates | Check ping frequency/schedule | Increase frequency or verify schedule matches active hours |
| No logs in app | Healthcheck query param not working | Verify `st.query_params.get("healthcheck")` in app.py |
| High GitHub Actions usage | Too many runs | Reduce frequency or restrict to weekdays only |

### Customization

**Change schedule** (edit `keepalive.yml`):
```yaml
schedule:
  - cron: "0 9-21 * * *"  # Every hour, 9am-9pm UTC
```

**Change frequency**:
```yaml
schedule:
  - cron: "*/30 15-23 * * *"  # Every 30 minutes
```

**Restrict to weekdays only**:
```yaml
schedule:
  - cron: "0 15-23 * * 1-5"  # Mon-Fri only
```

### Cost Analysis

**GitHub Actions minutes**:
- ~16 runs per day (7am-10pm = 16 hours)
- ~1 minute per run
- **~480 minutes/month**
- Free tier: 2,000 minutes/month ✅

**Streamlit resources**:
- Minimal load (simple GET request)
- App already optimized with caching
- No data mutations on healthcheck requests

### Future Improvements

Potential enhancements (not currently implemented):

- [ ] Add response time tracking
- [ ] Alert on consecutive failures
- [ ] Adaptive scheduling based on user traffic patterns
- [ ] Multi-region health checks for global availability
- [ ] Dedicated `/health` endpoint (requires app refactor)

### References

- [GitHub Actions Cron Syntax](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule)
- [Streamlit Community Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- Oracle security review: Thread T-e7041b4b-e2db-4844-a66a-9999ce72db97
