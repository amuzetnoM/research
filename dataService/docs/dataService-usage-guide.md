# DataService Usage Guide

This document provides comprehensive guidance on using the dataService abstraction for all frontend data operations.

## Basic Usage

### Fetching Data

```javascript
import { dataService } from '../services/dataService';

// Simple GET request
const userData = await dataService.fetchData('users/profile');

// GET with query parameters
const searchResults = await dataService.fetchData('search', { 
  query: 'keyword', 
  limit: 10 
});
```

### Creating Data

```javascript
const newUser = {
  name: 'John Doe',
  email: 'john@example.com',
  role: 'user'
};

const createdUser = await dataService.createData('users', newUser);
```

### Updating Data

```javascript
const updates = {
  name: 'John Updated',
  preferences: { theme: 'dark' }
};

await dataService.updateData('users/profile', updates);
```

### Deleting Data

```javascript
await dataService.deleteData('users/comments/123');
```

## Advanced Usage

### Working with Files

```javascript
const fileData = new FormData();
fileData.append('document', fileObject);
fileData.append('description', 'User manual');

await dataService.uploadFile('documents', fileData);
```

### Batch Operations

```javascript
const batchUpdates = [
  { id: 1, status: 'complete' },
  { id: 2, status: 'pending' },
  { id: 3, status: 'complete' }
];

await dataService.batchUpdate('tasks', batchUpdates);
```

### Handling Specific Errors

```javascript
try {
  await dataService.fetchData('restricted-data');
} catch (error) {
  if (error.status === 403) {
    // Handle permission error
  } else if (error.status === 404) {
    // Handle not found
  } else {
    // Handle other errors
  }
}
```

## Integration with React Hooks

### Creating Custom Data Hooks

```javascript
import { useState, useEffect } from 'react';
import { dataService } from '../services/dataService';

export const useResourceData = (resourceId) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await dataService.fetchData(`resources/${resourceId}`);
        setData(result);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [resourceId]);

  return { data, loading, error };
};
```

## Best Practices

1. **Always use the dataService for API communication** - Avoid direct fetch or axios calls
2. **Handle loading and error states** - Provide feedback to users during data operations
3. **Use appropriate methods** - Match HTTP methods to the right dataService methods
4. **Include error handling** - Wrap dataService calls in try/catch blocks
5. **Consider caching needs** - For frequently accessed data that doesn't change often

## Troubleshooting

### Common Errors

- **401 Unauthorized**: Check if the user is logged in and the token is valid
- **403 Forbidden**: Verify that the user has appropriate permissions
- **404 Not Found**: Ensure the endpoint exists and the resource ID is correct
- **Network Error**: Check internet connectivity and API server status

For additional support, refer to the API documentation or contact the development team.
