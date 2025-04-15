const { logger, errorMiddleware } = require('./errorHandler');
const path = require('path');

// Document-specific validation middleware
const validateDocumentRequest = (req, res, next) => {
  const errors = [];
  
  // Check if document title exists
  if (req.body.title && req.body.title.trim() === '') {
    errors.push('Document title cannot be empty');
  }
  
  // Check if document content exists
  if (req.body.content && req.body.content.trim() === '') {
    errors.push('Document content cannot be empty');
  }
  
  // Check if document type is valid
  const validTypes = ['article', 'tutorial', 'reference', 'guide'];
  if (req.body.type && !validTypes.includes(req.body.type)) {
    errors.push(`Invalid document type. Valid types are: ${validTypes.join(', ')}`);
  }

  if (errors.length > 0) {
    return res.status(400).json({ errors });
  }

  next();
};

// Document access control middleware
const checkDocumentAccess = (req, res, next) => {
  // Example implementation - should be replaced with actual access control logic
  const documentId = req.params.id;
  const userId = req.user ? req.user.id : null;
  
  // Log access attempt
  logger.info('Document access attempt', {
    documentId,
    userId,
    path: req.path,
    method: req.method
  });
  
  // Implement your access control logic here
  // For example:
  // const hasAccess = checkUserAccessToDocument(userId, documentId);
  // if (!hasAccess) {
  //   return next(new AccessDeniedError('You do not have permission to access this document'));
  // }
  
  next();
};

// File type validation for documentation uploads
const validateFileUpload = (req, res, next) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }
  
  const allowedExtensions = ['.md', '.docx', '.pdf', '.txt'];
  const fileExt = path.extname(req.file.originalname).toLowerCase();
  
  if (!allowedExtensions.includes(fileExt)) {
    return res.status(400).json({ 
      error: `Invalid file type. Allowed types: ${allowedExtensions.join(', ')}` 
    });
  }
  
  // Log successful upload
  logger.info('File validation successful', {
    filename: req.file.originalname,
    filesize: req.file.size,
    mimetype: req.file.mimetype
  });
  
  next();
};

// Special handling for documentation search errors
const handleSearchErrors = (err, req, res, next) => {
  if (err.name === 'SearchSyntaxError') {
    logger.warn('Invalid search query', {
      query: req.query.q,
      error: err.message,
      user: req.user ? req.user.id : 'anonymous'
    });
    
    return res.status(400).json({
      error: 'Invalid search query syntax',
      message: process.env.NODE_ENV !== 'production' ? err.message : undefined,
      suggestions: [
        'Check for unbalanced quotes or parentheses',
        'Verify boolean operators (AND, OR, NOT)',
        'Try using simpler search terms'
      ]
    });
  }
  
  // Pass to the main error handler
  next(err);
};

module.exports = {
  validateDocumentRequest,
  checkDocumentAccess,
  validateFileUpload,
  handleSearchErrors,
  documentationErrorMiddleware: [handleSearchErrors, errorMiddleware]
};
