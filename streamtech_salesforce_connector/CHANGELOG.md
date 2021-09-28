# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [13.0.1.2.6] - 2021-09-29
   - [ADD] SF Update Type: 1 Update Billing Customer ID. API Integration: Odoo to SF Update of Billing Customer ID upon create of Accounts in Odoo
## [13.0.1.2.5] - 2021-09-27
   - [IMP] Added handling to be able to accept 0 as a value in the contract term from SalesForce

## [13.0.1.2.4] - 2021-09-22
   - [ADD] Added new field to pull from SF import of Products (Days_Duration__c) 
   - [ADD] Auto creation of Subscription Template for Prepaid plan type

## [13.0.1.2.3] - 2021-09-21
   - [ADD] Company setup upon creation of Contacts from SF Opportunity Pull
   - [ADD] Add value and flow for `Transfer` to Subscription Status

## [13.0.1.2.2] - 2021-09-20
   - [FIX] Added fix for sf import of products with N/A Facility Type
   - [FIX] Display of Product new fields in Subscription Product form

## [13.0.1.2.1] - 2021-09-15
   - [ADD] SF API Integration - Update Account

## [13.0.1.2.0] - 2021-09-08
   - [IMP] Added Salesforce group in Product record
   - [IMP] Added new field facility_type in Product record under Salesforce group
   - [IMP] Added new field plan_type in Product record under Salesforce group
   - [IMP] Added security access for new models created (product_plan_type and product_facility_type)
   - [IMP] Created form/tree views and added sub menu item under Inventory > Configuration > Products and Sales > Configuration > Products for Facility Type and Plan Type
   - [IMP] Updated SF Connector pulling of Products to include new fields (Facility Type and Plan Type)
   - [IMP] Added new field Job Order SMS ID > Username in CRM record
   - [IMP] Added new field Job Order SMS ID > Password in CRM record
   - [IMP] Updated SF Connector pulling of Opportunities to include new fields (Job Order SMS ID Username and Password)
   - [IMP] added Is_Sandbox checkbox

## [13.0.1.1.3] - 2021-08-13
   - [IMP] Updated sf_type selection field values

## [13.0.1.1.2] - 2021-08-12
   - [IMP] Updated debug logs to error logs to be able to view in log file
   - [IMP] Added handling for duplicate city values

## [13.0.1.1.1] - 2021-08-09
   - [IMP] Added logs and updated warnings for no active products found and pulling of accounts without opportunities
   - [IMP] Added handling for multiple records found in Odoo via salesforce_id
   - [IMP] Enhancement: Remove the SF Connector Condition to limit the pull of Opportunities based on Created Date
   - [IMP] Added handling for already completed opportunity and archived products in Odoo side

## [13.0.1.1.0] - 2021-07-29
   - [IMP] Salesforce Connector Enhancement for Pulling of Products, Accounts and Opportunities

## [13.0.1.0.3] - 2021-03-29
   - Added importing for partner model

## [13.0.1.0.2] - 2021-03-28
   - Changed SF-based CRM form fields to read only: email, phone 

## [13.0.1.0.1] - 2021-03-28
   - Changed additional CRM form fields to read only if values are from SalesForce
   - Changed additional Customer form fields to read only if values are from SalesForce

