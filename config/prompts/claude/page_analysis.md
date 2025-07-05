# Claude Page Analysis Prompt
# Used to analyze a web page and understand its structure

Analyze the provided web page and extract comprehensive information for test generation. Focus on:

## 1. Page Structure Analysis
- Identify the page type (login, dashboard, form, listing, etc.)
- Map the overall layout and main sections
- Detect navigation elements and menus
- Find forms and their purposes
- Locate interactive elements (buttons, links, dropdowns)

## 2. Element Identification
For each significant element, provide:
- Selector (prefer data-testid > id > class > other)
- Element type (button, input, link, etc.)
- Associated text or label
- Current state (enabled, visible, etc.)
- Parent-child relationships

## 3. User Interactions
Identify all possible user actions:
- Clickable elements and their destinations
- Form inputs and their validation rules
- Hover effects and tooltips
- Keyboard shortcuts
- Drag and drop functionality

## 4. Dynamic Behavior
Detect dynamic elements:
- AJAX calls and API endpoints
- Real-time updates
- Loading states
- Error messages
- Success notifications

## 5. Authentication & Authorization
Check for:
- Login/logout functionality
- Protected routes
- Role-based access
- Session management

## 6. Data Patterns
Identify:
- Data tables and lists
- Pagination
- Sorting and filtering
- Search functionality
- CRUD operations

## Return Format
Provide analysis as structured JSON:
```json
{
  "page_info": {
    "url": "string",
    "title": "string",
    "type": "string"
  },
  "elements": [
    {
      "selector": "string",
      "type": "string",
      "text": "string",
      "attributes": {},
      "interactive": boolean
    }
  ],
  "forms": [],
  "navigation": [],
  "api_endpoints": [],
  "user_flows": [],
  "test_scenarios": []
}
```