# CybrScan Scanner Options

To solve persistent issues with blank screens in the scanner, we've implemented multiple fallback options with increasing levels of reliability.

## Available Scanner Versions

### 1. Standard Scanner
- **URL**: `/scanner/<scanner_uid>/embed`
- **Features**: Full functionality, branding, customization
- **Dependencies**: JavaScript, CSS, Bootstrap

### 2. Universal Scanner
- **URL**: `/scanner/<scanner_uid>/universal` or `/universal-scanner`
- **Features**: Self-contained, error recovery, simplified interface
- **Dependencies**: Minimal JavaScript, basic CSS

### 3. Minimal Scanner
- **URL**: `/scanner/<scanner_uid>/minimal` or `/minimal-scanner`
- **Features**: Ultra-lightweight, guaranteed to work
- **Dependencies**: None (HTML-only, no JavaScript)

## How to Use

### For End Users

If you experience blank screens or other issues with the scanner:

1. **Try Direct Access**:
   - Access the universal scanner: `/scanner/<scanner_uid>/universal`
   - Access the minimal scanner: `/scanner/<scanner_uid>/minimal`

2. **Use Emergency Parameter**:
   - Add `?emergency=true` to any scanner URL:
   - Example: `/scanner/<scanner_uid>/embed?emergency=true`

3. **Specify Mode**:
   - Use `/scanner/<scanner_uid>/embed?mode=universal`
   - Use `/scanner/<scanner_uid>/embed?mode=minimal`

### For Administrators

You can embed any version of the scanner in your website:

#### Standard Scanner (Regular embed):
```html
<iframe src="https://example.com/scanner/<scanner_uid>/embed" 
        width="100%" height="600" frameborder="0"></iframe>
```

#### Universal Scanner (More reliable):
```html
<iframe src="https://example.com/scanner/<scanner_uid>/universal" 
        width="100%" height="600" frameborder="0"></iframe>
```

#### Minimal Scanner (Most reliable):
```html
<iframe src="https://example.com/scanner/<scanner_uid>/minimal" 
        width="100%" height="600" frameborder="0"></iframe>
```

### Automatic Fallback

All scanner versions include automatic fallback mechanisms:

1. The standard scanner will detect blank screens and redirect to the universal scanner
2. If the universal scanner fails, it will redirect to the minimal scanner
3. The minimal scanner has no dependencies and is guaranteed to work

## Technical Details

### Blank Screen Detection

We've implemented multiple layers of blank screen detection:

1. **Ultra-Early Detection**: Loads before anything else, checks DOM structure
2. **Content Monitoring**: Actively monitors for visible content
3. **Form Detection**: Ensures the scan form is present and visible
4. **Error Handling**: Catches JavaScript errors and redirects if necessary

### Recovery Mechanisms

When issues are detected:

1. First attempt: Show fallback UI with a redirect button
2. Second attempt: Automatic redirect to appropriate scanner version
3. Final fallback: Direct link to minimal scanner without parameters

## Troubleshooting

If all scanner versions fail:

1. Check server logs for backend errors
2. Ensure the `/fixed_scan` endpoint is working correctly
3. Verify database connections are functioning
4. Check network connectivity and CORS configuration

## Additional Notes

- The minimal scanner uses the same `/fixed_scan` endpoint as other versions
- All scanners include the scanner_id and client_id in form submission
- The minimal scanner will work even without JavaScript enabled