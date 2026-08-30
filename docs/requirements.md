# Salary Management — Requirements

**Version:** 0.1
**Status:** Provisional — awaiting clarification on selected product requirements

## Goal

Build a web-based salary management application for ACME's HR Manager to efficiently manage compensation information for an organization of approximately 10,000 employees distributed across multiple countries.

The application should replace tedious spreadsheet-driven salary management with a clear, reliable, searchable, and maintainable software workflow while enabling HR to derive useful information about how employees are compensated.

## Primary User

**HR Manager**

The initial product is designed around the workflows and information needs of an HR Manager rather than employee self-service.

## Core Scope

The initial application will provide:

* storage and retrieval of employee compensation information;
* support for approximately 10,000 seeded employees;
* searchable and filterable employee salary data;
* paginated access to employee records;
* viewing of employee compensation information;
* modification of salary information subject to validation;
* useful aggregate compensation information for HR;
* a React-based web interface;
* an API/backend service;
* persistent relational storage;
* deterministic seed data;
* meaningful automated tests covering core behaviour.

## Compensation Data

Salary values will be represented using decimal-safe financial types rather than floating-point arithmetic.

Employees may belong to different countries and currencies.

The precise treatment of cross-currency organization-wide analytics is pending clarification from Incubyte.

## Product Principles

The product should prioritize:

* correctness;
* clear HR workflows;
* fast discovery of relevant employee information;
* understandable compensation insights;
* safe editing of salary data;
* predictable validation and error behaviour;
* maintainability over unnecessary architectural complexity.

## Explicitly Out of Scope for the Initial Submission

Unless clarification from Incubyte changes the requirement, the following are deliberately excluded:

* payroll execution or bank transfers;
* income-tax calculation;
* statutory payroll processing;
* payslip generation;
* attendance management;
* leave management;
* benefits administration;
* recruitment functionality;
* employee self-service;
* enterprise SSO integration;
* complex role-based access-control infrastructure;
* distributed/microservice architecture;
* event streaming or message queues;
* AI/LLM functionality added solely for demonstration purposes.

These are adjacent HR/payroll concerns but are not necessary to solve the stated salary-management problem and would increase complexity without corresponding product value.

## Pending Clarifications

The following questions have been sent to Incubyte:

1. Whether “manage salary data” primarily means managing current employee compensation or also requires salary history, compensation components, and/or bulk import/export.
2. Representative examples of the questions HR should be able to answer about organizational compensation, including whether a natural-language/AI interface is expected.
3. Whether multi-country salaries should remain in local currencies or be normalized to a common reporting currency.
4. Whether authentication/authorization must be implemented or whether an authenticated HR Manager context may be assumed.

These questions may alter feature scope but do not prevent project setup, testing infrastructure, architecture preparation, or implementation of universally required employee-management capabilities.

## Non-Functional Expectations

The system should:

* remain responsive with 10,000 employee records;
* avoid transferring the entire employee dataset to the browser unnecessarily;
* use appropriate database indexes for common lookup/filter operations;
* validate inputs on the backend regardless of frontend validation;
* use clear HTTP semantics and error responses;
* preserve financial precision;
* have fast, deterministic, understandable automated tests;
* be reproducible from documented setup instructions;
* be deployable as a fully functional web application.

## Success Criteria

A reviewer should be able to:

1. clone the repository;
2. follow the README successfully;
3. initialize the database;
4. seed 10,000 employees;
5. start the backend and frontend;
6. browse/search/filter employee compensation data;
7. perform supported salary-management operations;
8. obtain useful compensation insights;
9. run the automated test suite successfully;
10. understand the major engineering decisions and trade-offs from the repository artifacts.
