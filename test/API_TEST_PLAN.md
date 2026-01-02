# API Test Plan – InvParser

## What to test
The following API endpoints will be tested:

- POST /extract  
  - Successful invoice extraction  
  - Invalid or missing file handling  

- GET /invoice/{invoice_id}  
  - Retrieve existing invoice  
  - Invoice not found (404)

- GET /vendor/{vendor_name}  
  - Retrieve invoices by vendor  
  - Vendor not found

## Test design strategy
Integration testing strategy is used.
The API endpoints are tested using FastAPI TestClient while interacting with a real SQLite database.
External services such as OCI Document AI are mocked to avoid dependency on external systems.
Tests are implemented using the unittest framework.

## Test environment
Tests are executed locally and automatically in GitHub Actions CI.

## Success criteria
- 100% API endpoint coverage  
- As close as possible to 100% API code coverage  
- All tests pass successfully  
- Code coverage is reported in GitHub pull requests  

## Reporting
Test execution results and code coverage are reported using pytest, pytest-cov and Codecov.
