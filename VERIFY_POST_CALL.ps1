param(
    [Parameter(Mandatory = $true)]
    [string]$ConversationId,

    [string]$BaseUrl = "https://frontdesk-lab.easyaigent.com",

    [string]$ToolApiKey = $env:TOOL_API_KEY
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ToolApiKey)) {
    throw "TOOL_API_KEY is required. Set it in the environment or pass -ToolApiKey."
}

$headers = @{
    Authorization = "Bearer $ToolApiKey"
}

$url = "$BaseUrl/v1/ops/post-call-events/$ConversationId"
Write-Host "Verifying signed post-call processing for $ConversationId ..."

$response = Invoke-RestMethod -Method Get -Uri $url -Headers $headers
$response | ConvertTo-Json -Depth 10
