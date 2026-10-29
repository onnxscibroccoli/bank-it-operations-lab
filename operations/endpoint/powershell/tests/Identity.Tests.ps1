BeforeAll {
    $script:identityScript = Join-Path $PSScriptRoot '../Invoke-LabIdentityChange.ps1'
}
Describe 'Offline lifecycle plans' {
    It 'labels each action as a non-executing plan' -ForEach @('joiner','mover','leaver') {
        $result = & $identityScript -Action $_ -UserPrincipalName 'alex@lab.example' | ConvertFrom-Json
        $result.mode | Should -Be 'PLAN_ONLY'
        $result.executed | Should -BeFalse
        $result.mutationsExecuted | Should -Be 0
        $result.action | Should -Be $_
        $result.steps.Count | Should -BeGreaterThan 0
    }
    It 'disables and revokes before removing access' {
        $result = & $identityScript -Action leaver -UserPrincipalName 'alex@lab.example' | ConvertFrom-Json
        $result.steps[0] | Should -Be 'disable-account'
        $result.steps[1] | Should -Be 'revoke-sessions'
        $result.steps[2] | Should -Be 'remove-privileged-groups'
    }
    It 'rejects real-domain and malformed identities' -ForEach @('alex@example.com','a@lab.example.evil','a b@lab.example','$(whoami)@lab.example','') {
        { & $identityScript -Action joiner -UserPrincipalName $_ } | Should -Throw
    }
    It 'rejects unsupported actions' {
        { & $identityScript -Action delete -UserPrincipalName 'alex@lab.example' } | Should -Throw
    }
}
