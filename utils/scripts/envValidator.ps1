$envFile = Get-Content ".\.env.template"

$envFile -split "=" | Where-Object {$_ -notmatch '\"'} | Set-Content ".\envVarsbefSpl.txt"
Get-Content ".\envVarsbefSpl.txt" | Where-Object {$_ -notmatch '\#'} | Set-Content ".\envVarsN.txt"
Get-Content ".\envVarsN.txt" | Where-Object {$_ -ne ''} | Set-Content ".\video_creation\data\envvars.txt"
Remove-Item ".\envVarsbefSpl.txt"
Remove-Item ".\envVarsN.txt"

Write-Host $nowSplit
