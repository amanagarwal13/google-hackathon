# Flask ADK Agent Server - Changelog

## [1.0.1] - 2024-01-XX

### Fixed
- **Template Error**: Fixed `UndefinedError: 'moment' is undefined` in Jinja2 template
  - Removed server-side `moment()` usage in `templates/index.html`
  - Added JavaScript function `updateTemplateTimestamps()` to handle client-side timestamp formatting
  - Timestamps are now properly formatted using JavaScript's built-in `Date` functions

### Changed
- Template timestamps are now handled entirely on the client side for better performance
- Added `current_time` context variable to template for future use

## [1.0.0] - 2024-01-XX

### Added
- Initial Flask ADK Agent Server implementation
- Google Cloud Application Default Credentials authentication (same as Oracle Agent)
- Real-time WebSocket communication with Socket.IO
- Modern responsive chat interface
- Session management and persistence
- Production-ready deployment with Gunicorn/Waitress
- Comprehensive health checks and authentication status endpoints
- Oracle Agent compatibility and Fi MCP integration 