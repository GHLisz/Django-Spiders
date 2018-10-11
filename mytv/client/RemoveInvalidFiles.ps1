$path = "\\111"

Get-ChildItem -Path $path -Recurse -File | Where-Object {$_.Length -lt 10kb} | % {
    Write-Host $_.FullName
    Remove-Item $_.FullName
}