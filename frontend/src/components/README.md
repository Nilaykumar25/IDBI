# Reusable UI Components

## Error Handling and User Feedback Components

### ErrorMessage Component

**Location:** `frontend/src/components/ErrorMessage.jsx`

A flexible error message component that displays user-friendly error messages with optional retry functionality.

**Props:**
- `message` (string, required): The error message to display
- `type` (string): Display type - 'error', 'warning', or 'info' (default: 'error')
- `severity` (string): Alternative to `type` for backwards compatibility
- `title` (string): Optional title for the error
- `details` (string): Technical details (shown in monospace)
- `onDismiss` (function): Callback for dismissing the error
- `onRetry` (function): Callback for retry action (shows retry button if provided)
- `className` (string): Additional CSS classes

**Usage:**
```jsx
<ErrorMessage 
  message="Failed to load data"
  type="error"
  title="Connection Error"
  onRetry={() => fetchData()}
  onDismiss={() => setError(null)}
/>
```

### LoadingSpinner Component

**Location:** `frontend/src/components/LoadingSpinner.jsx`

A consistent loading indicator for async operations.

**Props:**
- `size` (string): 'small', 'medium', or 'large' (default: 'medium')
- `message` (string): Loading message to display
- `fullScreen` (boolean): Whether to display as full-screen overlay

**Usage:**
```jsx
<LoadingSpinner 
  size="large" 
  message="Computing financial health score..." 
/>
```

### RetryButton Component

**Location:** `frontend/src/components/RetryButton.jsx`

A reusable retry button with loading states.

**Props:**
- `onRetry` (function, required): Callback when retry is clicked
- `loading` (boolean): Whether retry operation is in progress
- `message` (string): Button text (default: 'Retry')
- `size` (string): 'small', 'medium', or 'large'
- `variant` (string): 'primary' or 'secondary'

**Usage:**
```jsx
<RetryButton 
  onRetry={() => handleRetry()} 
  loading={isRetrying}
  size="small"
/>
```

## API Client Enhancements

**Location:** `frontend/src/lib/api.js`

Enhanced API client with:

- **Automatic retries**: Retries transient errors (5xx, network errors, timeouts) up to 2 times with exponential backoff
- **Error transformation**: Converts backend errors into user-friendly messages via `transformError()` function
- **Authentication handling**: Automatically injects JWT tokens and redirects on 401 errors
- **Timeout management**: 30-second request timeout

**Exported utilities:**
- `apiClient`: Axios instance configured with interceptors
- `transformError(error)`: Transforms API errors into user-friendly format
- `callAPI(apiFunction)`: Wrapper for API calls with standardized response format

**Error Response Format:**
```javascript
{
  message: "User-friendly error message",
  severity: "error" | "warning" | "info",
  retryable: boolean,
  technical: "Technical error details"
}
```

## Implementation in Dashboard Views

All dashboard views now include:

1. **Error display**: Using ErrorMessage component with user-friendly messages
2. **Loading states**: LoadingSpinner during async operations
3. **Retry functionality**: RetryButton for failed operations
4. **Partial data warnings**: Warnings when data sources are unavailable
5. **Missing data indicators**: Visual indicators for missing/failed data sources

### Views Updated:
- MSMESearch.jsx
- DataSources.jsx
- TrendAnalysis.jsx
- RiskFactors.jsx
- WhatIfSimulator.jsx
- Recommendations.jsx (already had good error handling)
- EcosystemIntegration.jsx (already had good error handling)

## Best Practices

1. **Always use transformError()** when catching API errors:
   ```javascript
   catch (error) {
     const transformedError = transformError(error)
     setError(transformedError)
   }
   ```

2. **Provide retry for transient errors**:
   ```javascript
   {error && error.retryable && (
     <ErrorMessage
       message={error.message}
       onRetry={() => handleRetry()}
     />
   )}
   ```

3. **Show loading states during operations**:
   ```javascript
   {loading && <LoadingSpinner message="Loading data..." />}
   ```

4. **Handle partial data gracefully**:
   ```javascript
   {missingDataSources.length > 0 && (
     <ErrorMessage
       type="warning"
       message="Some data sources unavailable. Score computed with remaining sources."
     />
   )}
   ```
