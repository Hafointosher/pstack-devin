param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args_)
node (Join-Path $PSScriptRoot 'log.mjs') @Args_
exit $LASTEXITCODE
