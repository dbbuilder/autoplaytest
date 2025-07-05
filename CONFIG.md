anguage.googleapis.com/v1"
  
models:
  default: "gemini-1.5-pro"
  available:
    - name: "gemini-1.5-pro"
      max_tokens: 8192
      supports_vision: true
      cost_per_1k_input: 0.00125
      cost_per_1k_output: 0.00375

request_params:
  temperature: 0.2
  max_output_tokens: 8192
  top_p: 0.95
  top_k: 40
  candidate_count: 1
  
safety_settings:
  - category: "HARM_CATEGORY_HARASSMENT"
    threshold: "BLOCK_NONE"
  - category: "HARM_CATEGORY_HATE_SPEECH"
    threshold: "BLOCK_NONE"
    
rate_limits:
  requests_per_minute: 60
  tokens_per_minute: 60000
  concurrent_requests: 10
  
features:
  supports_system_prompt: true
  supports_function_calling: true
  supports_vision: true
  supports_streaming: true
  max_context_window: 1000000
```

### GPT Configuration

Location: `config/ai_providers/gpt.yaml`

```yaml
provider:
  name: "gpt"
  display_name: "OpenAI GPT-4"
  api_base_url: "https://api.openai.com/v1"
  
models:
  default: "gpt-4-turbo-preview"
  available:
    - name: "gpt-4-turbo-preview"
      max_tokens: 4096
      supports_vision: true
      cost_per_1k_input: 0.01
      cost_per_1k_output: 0.03

request_params:
  temperature: 0.2
  max_tokens: 4096
  top_p: 0.95
  frequency_penalty: 0
  presence_penalty: 0
  
rate_limits:
  requests_per_minute: 60
  tokens_per_minute: 90000
  concurrent_requests: 10
  
features:
  supports_system_prompt: true
  supports_function_calling: true
  supports_vision: true
  supports_streaming: true
  max_context_window: 128000
```

## Prompt Templates

Prompt templates are stored as Markdown files in `config/prompts/{provider}/`

### System Prompt

Location: `config/prompts/{provider}/system_prompt.md`

This file contains the main instructions for the AI model about its role as a TDD test generator.

Key sections:
- Core principles (TDD methodology)
- Code style requirements
- Test categories to generate
- Expected output format

### Page Analysis Prompt

Location: `config/prompts/{provider}/page_analysis.md`

Instructions for analyzing web pages:
- Page structure analysis
- Element identification
- User interaction detection
- Dynamic behavior analysis
- Authentication detection

### Test Generation Prompt

Location: `config/prompts/{provider}/test_generation.md`

Template for generating tests:
- Context placeholders ({page_analysis}, {test_type}, etc.)
- Test structure requirements
- TDD approach instructions
- Assertion patterns
- Best practices

## Test Configuration

### Command Line Arguments

```bash
# Basic usage
run.bat --url https://example.com --username user --password pass --mode generate --output-dir ./tests

# Advanced options
run.bat \
  --url https://example.com \
  --username user \
  --password pass \
  --mode generate \
  --output-dir ./tests \
  --ai-provider claude \
  --test-types login navigation form_interaction \
  --browser chromium \
  --headless \
  --parallel \
  --max-workers 4 \
  --timeout 60000 \
  --config ./custom-config.yaml
```

### Test Types

Available test types and their focus:

| Test Type | Description | Key Scenarios |
|-----------|-------------|---------------|
| `login` | Authentication flows | Valid/invalid credentials, session management |
| `navigation` | Page routing | Menu navigation, breadcrumbs, deep links |
| `form_interaction` | Form handling | Validation, submission, error states |
| `search` | Search functionality | Queries, filters, sorting |
| `crud_operations` | Data operations | Create, read, update, delete |
| `api_integration` | API testing | Endpoints, responses, error handling |
| `accessibility` | A11y compliance | ARIA, keyboard nav, screen readers |
| `performance` | Performance testing | Load times, resource usage |
| `visual_regression` | Visual testing | Layout, responsive design |
| `e2e_workflow` | End-to-end flows | Complete user journeys |

## Advanced Settings

### Custom Configuration

Create custom configuration files:

```yaml
# custom-config.yaml
extends: "./config/config.yaml"  # Inherit from base config

# Override specific settings
ai_providers:
  default_provider: "gpt"
  
test_generation:
  test_types:
    - login
    - api_integration
    
test_execution:
  headless: false
  slow_mo: 500  # Slow down for debugging
```

### Page Object Configuration

Configure Page Object Model generation:

```yaml
page_objects:
  enabled: true
  base_class: "BasePage"
  naming_convention: "{PageName}Page"
  directory: "./page_objects"
  
  methods:
    wait_timeout: 30000
    retry_count: 3
    screenshot_on_error: true
```

### Network Configuration

Configure network behavior:

```yaml
network:
  offline: false
  throttling:
    download: 1000000  # 1Mbps
    upload: 500000     # 500Kbps
    latency: 50        # 50ms
    
  request_interception:
    enabled: true
    block_resources:
      - "font"
      - "image"
    
  har_recording:
    enabled: true
    path: "./network_logs"
```

### Database Configuration

If using database features:

```yaml
database:
  enabled: true
  connection_string: "${DATABASE_URL}"
  
  tables:
    test_results: "test_results"
    test_sessions: "test_sessions"
    test_metrics: "test_metrics"
    
  retention:
    days: 30
    cleanup_on_start: true
```

## Troubleshooting

### Common Configuration Issues

#### 1. API Key Not Found

**Error**: `ValueError: Claude API key not found in environment variables`

**Solution**:
```bash
# Windows
set ANTHROPIC_API_KEY=your-api-key

# Linux/Mac
export ANTHROPIC_API_KEY=your-api-key
```

#### 2. Model Not Available

**Error**: `Model 'claude-3-opus' not available`

**Solution**: Update model name in configuration:
```yaml
claude:
  model: "claude-3-opus-20240229"  # Use full model name
```

#### 3. Rate Limit Exceeded

**Error**: `Rate limit exceeded`

**Solution**: Adjust rate limits in provider config:
```yaml
rate_limits:
  requests_per_minute: 30  # Lower the limit
  concurrent_requests: 2   # Reduce concurrent requests
```

#### 4. Timeout Issues

**Error**: `Request timed out`

**Solution**: Increase timeouts:
```yaml
timeout: 60  # Increase to 60 seconds

test_execution:
  timeout: 60000  # Increase test timeout
```

### Validation

Validate your configuration:

```python
# validate_config.py
import yaml
from pathlib import Path

def validate_config(config_path):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Check required fields
    assert 'ai_providers' in config
    assert 'test_generation' in config
    assert 'test_execution' in config
    
    print("✅ Configuration is valid!")

if __name__ == "__main__":
    validate_config("config/config.yaml")
```

### Debug Mode

Enable debug mode for detailed logging:

```yaml
debug:
  enabled: true
  log_api_calls: true
  save_raw_responses: true
  response_dir: "./debug/responses"
  
logging:
  level: "DEBUG"
  log_api_requests: true
  log_api_responses: true
```

## Best Practices

1. **Use Environment Variables for Secrets**
   - Never commit API keys to version control
   - Use `.env` files for local development

2. **Start with Default Configuration**
   - The default settings work well for most cases
   - Only customize what you need

3. **Version Your Configuration**
   - Keep config files in version control
   - Document changes in commit messages

4. **Test Configuration Changes**
   - Run validation after changes
   - Test with a simple page first

5. **Monitor API Usage**
   - Track token usage
   - Set up alerts for rate limits

6. **Optimize for Cost**
   - Use appropriate models for tasks
   - Cache responses when possible
   - Batch similar requests

## Configuration Examples

### Minimal Configuration

```yaml
# Minimal working configuration
ai_providers:
  default_provider: "claude"

test_generation:
  test_types:
    - login
    - navigation

test_execution:
  browsers:
    - chromium
```

### Performance Testing Focus

```yaml
# Configuration for performance testing
test_generation:
  test_types:
    - performance
    - api_integration
    
performance:
  page_load_threshold: 1000  # Strict 1s limit
  measure_metrics:
    - first_paint
    - first_contentful_paint
    - largest_contentful_paint
    - time_to_interactive
```

### Accessibility Testing Focus

```yaml
# Configuration for accessibility testing
test_generation:
  test_types:
    - accessibility
    - navigation
    
page_analysis:
  accessibility_checks:
    - color_contrast
    - aria_labels
    - keyboard_navigation
    - screen_reader_compatibility
```

### Multi-Provider Configuration

```yaml
# Use different providers for different tasks
ai_providers:
  page_analysis_provider: "gemini"  # Better for analysis
  test_generation_provider: "claude"  # Better for code
  validation_provider: "gpt"  # Better for validation
```

## Updates and Migration

When updating configuration:

1. **Backup Current Configuration**
   ```bash
   cp config/config.yaml config/config.yaml.backup
   ```

2. **Check Migration Guide**
   - Review CHANGELOG.md for breaking changes
   - Update deprecated options

3. **Test with Dry Run**
   ```bash
   run.bat --dry-run --config new-config.yaml
   ```

4. **Gradual Rollout**
   - Test with one test type first
   - Expand to full suite

This configuration system provides flexibility while maintaining sensible defaults. Start simple and add complexity as needed.