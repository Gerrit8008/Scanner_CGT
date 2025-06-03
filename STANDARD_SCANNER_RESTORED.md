# Standard Scanner Restored

The standard scanner has been restored as the default experience, while maintaining subtle recovery options for users who experience issues.

## Changes Made

1. **Restored standard scanner as default**
   - The standard scanner is now the default experience for all users
   - Alternative scanner versions are only used when explicitly requested

2. **Subtle recovery options**
   - Added a small "Scanner Help" button in the bottom-right corner
   - It's semi-transparent until hovered over to be less intrusive
   - Issues detection now shows options instead of forcing redirects

3. **No automatic redirects**
   - Removed automatic redirects to alternative scanner versions
   - Users now have control over which scanner version they use
   - Blank screen detection shows options instead of redirecting

## Available Scanner Versions

All scanner versions are still available, but now they're opt-in instead of being automatically triggered:

1. **Standard Scanner** (default)
   - `/scanner/<scanner_uid>/embed`
   - Full features and branding

2. **Universal Scanner** (manual option)
   - `/scanner/<scanner_uid>/universal`
   - More reliable with self-contained error handling

3. **Minimal Scanner** (manual option)
   - `/scanner/<scanner_uid>/minimal`
   - Ultra-lightweight HTML-only version

## How Users Can Access Alternative Versions

1. **Help Button**
   - Small "Scanner Help" button in the bottom-right corner of standard scanner
   - Takes users to the Universal Scanner

2. **URL Parameters**
   - Add `?mode=universal` to use Universal Scanner
   - Add `?mode=minimal` to use Minimal Scanner
   - Add `?emergency=true` to use Minimal Scanner

3. **Scanner Options Page**
   - Accessible from client dashboard
   - Shows all available scanner versions
   - Provides embed codes for each version