Feature: API Health Check
  As a developer
  I want to check if the API is healthy
  So that I can ensure the service is running properly

  Scenario: API health check
    Given the API server is running
    When I check the health endpoint
    Then I should get a healthy status
