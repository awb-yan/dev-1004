# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [13.0.1.5.7] - 2021-09-22
- [FIX] Datetime(timezone) passed from Odoo to SF in Update Account
- [FIX] Datetime(timezone) in Expiry Notification
- [ADD] Start and End Date Subscription Prepaid
- [MISC] Updated implementation of _get_last_subscrption

## [13.0.1.5.6] - 2021-09-21
- [FIX] Temporary discon due to Expiry - Stage InProgress to Closed
- [ADD] Activation Portal
- [FIX] Update New Subscription with Opportunity ID from Last Subscription
- [FIX] Subscription Stage changed from In Progress to Closed

## [13.0.1.5.5] - 2021-09-21
- [FIX] Update New Subscription with Opportunity ID from Last Subscription
- [IMP] ATM Ref Generation : Inherit from the last Subscription ATM Ref
- [IMP] Subscription Stage changed from In Progress to Closed
- [FIX] Include date and time in updating Subscription Start Date 
- [IMP] Organize and Optimize Disconnection Logic
- [ADD] Added plan type in Subscription record
- [FIX] Temporary discon due to Expiry - Stage InProgress to Closed
- [ADD] Activation Portal

## [13.0.1.5.4] - 2021-09-20
- [FIX] Populate PrepaidIndicator flag in the Aradial Create User payload
- [MISC] Proper logging for the debug logs
- [FIX] SF API Update Account trigger
- [ADD] Update of latest subscription upon reloading


## [13.0.1.5.3] - 2021-09-16
- [FIX] Handling for Main Plan in Postpaid subscription
- [FIX] Error in SMS Sending
- [ADD] Debug Logs

## [13.0.1.5.2] - 2021-09-15
- [ADD] SF API integration and trigger in creation of Subscription

## [13.0.1.5.1] - 2021-09-15
- [FIX] Added missing fields (Removed last night)
- [ADD] New field datetime for the TMS Notification

## [13.0.1.5.0] - 2021-09-08
- [IMP] SMS Provisioning and Activation flows
- [ADD] Disconnection API

## [13.0.1.4.0] - 2021-06-10

- [IMP] atm ref on subscription

## [13.0.1.3.0] - 2021-05-14

- [IMP] Add Date range in Subscription Line

## [13.0.1.2.0] - 2021-04-07

- [IMP] Proration Computation

## [13.0.1.1.0] - 2021-03-25

- Add customer number

# v1.1.0

    - [IMP] Add Rebates in Statement line