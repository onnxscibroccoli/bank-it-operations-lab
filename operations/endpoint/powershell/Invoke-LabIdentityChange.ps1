#Requires -Version 5.1
<#
.SYNOPSIS
  Synthetic joiner / mover / leaver. Not executed in this lab.
.DESCRIPTION
  Reads a JSON request and prints the Graph/AD actions it would take.
  Refuses secret material. Does not call Microsoft or Active Directory.
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [ValidateSet('joiner', 'mover', 'leaver')]
  [string] $Action,
  [Parameter(Mandatory = $true)]
  [string] $UserPrincipalName
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($UserPrincipalName -notmatch '^[^@\s]+@lab\.example$') {
  throw "UPN must be a lab.example address"
}

$privileged = @('Role-DomainAdmins', 'Role-GlobalAdmin')

switch ($Action) {
  'joiner' {
    [pscustomobject]@{
      action = 'joiner'
      upn    = $UserPrincipalName
      steps  = @(
        'create-disabled-account',
        'assign-single-job-role',
        'require-mfa-registration',
        'enable-account'
      )
    } | ConvertTo-Json -Compress
  }
  'mover' {
    [pscustomobject]@{
      action = 'mover'
      upn    = $UserPrincipalName
      steps  = @('remove-previous-job-role', 'assign-single-job-role', 'record-access-review')
    } | ConvertTo-Json -Compress
  }
  'leaver' {
    [pscustomobject]@{
      action = 'leaver'
      upn    = $UserPrincipalName
      steps  = @(
        'disable-account',
        'revoke-sessions',
        'remove-privileged-groups',
        'remove-job-role',
        'retain-mailbox-per-policy'
      )
      removeGroups = $privileged
    } | ConvertTo-Json -Compress
  }
}
