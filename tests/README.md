# Pytest Configuration for LLMQuizer

## Running Tests

### Local Testing (with mock server)
```bash
# Run all tests
pytest -v

# Run specific test
pytest -v tests/test_main.py::test_boolean_answer

# Run with output
pytest -v -s
```

### Railway Deployment Testing
```bash
# Set environment variable to use Railway
USE_RAILWAY=true pytest -v

# Or on Windows PowerShell
$env:USE_RAILWAY="true"; pytest -v
```

## Test Categories

### Basic Tests
- `test_root_endpoint` - Root endpoint returns correct status
- `test_health_endpoint` - Health check endpoint
- `test_invalid_secret` - 403 for wrong secret
- `test_invalid_json` - 400 for malformed JSON
- `test_missing_fields` - 400 for missing required fields

### Answer Format Tests
- `test_boolean_answer` - Boolean type handling
- `test_json_object_answer` - JSON object with multiple fields
- `test_number_answer` - Integer/float answers
- `test_string_answer` - String answers

### File Type Tests
- `test_csv_processing` - CSV file download and analysis
- `test_pdf_processing` - PDF file processing
- `test_image_processing` - Image analysis with Gemini

### Quiz Chain Tests
- `test_wrong_answer_with_next_url` - Continue after wrong answer
- `test_quiz_chain_stops_without_url` - Stop when no next URL
- `test_full_quiz_chain` - Complete multi-step quiz

### Edge Case Tests
- `test_broken_link_graceful_failure` - Handle 404 file links
- `test_404_not_found` - Non-existent endpoints

## Test Coverage

| Feature | Test Count | Status |
|---------|-----------|--------|
| HTTP Status Codes | 4 | ✅ |
| Answer Formats | 4 | ✅ |
| File Processing | 3 | ✅ |
| Quiz Chain Logic | 3 | ✅ |
| Edge Cases | 2 | ✅ |
| **Total** | **16** | ✅ |

## Environment Variables

- `USE_RAILWAY` - Set to "true" to test against Railway deployment
- `RAILWAY_URL` - Railway deployment URL (default: https://llmquizer-production.up.railway.app)
- `MY_SECRET` - Secret for authentication (default: "test-secret" for local tests)

## Test Fixtures

- `mock_server` - Starts local mock quiz server on port 8001
- `main_app_server` - Starts main FastAPI app on port 8000 (or uses Railway)
- `client` - Async HTTP client for making requests
- `clear_mock_server_log` - Clears mock server log before each test

## Expected Test Duration

- Individual tests: 5-30 seconds
- Full suite (local): ~2-3 minutes
- Full suite (Railway): ~3-5 minutes (network latency)

## Troubleshooting

### Tests timing out
- Increase `max_wait` in `wait_for_submissions()`
- Check if API keys are set in `.env`
- Verify mock server is running

### Mock server connection errors
- Ensure port 8001 is available
- Check firewall settings
- Restart mock server manually: `python mock_server.py`

### Railway tests failing
- Verify Railway deployment is running
- Check `RAILWAY_URL` is correct
- Ensure Railway has correct environment variables set
