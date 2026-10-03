param(
    [Parameter(Mandatory=$true)][string]$Src,
    [Parameter(Mandatory=$true)][string]$Out
)
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $Out) { Remove-Item -LiteralPath $Out -Force }
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
$d = $w.Documents.Open($Src, $false, $true)
try { $d.ExportAsFixedFormat($Out, 17) } catch { $d.SaveAs([ref]$Out, [ref]17) }
'word pages: ' + $d.ComputeStatistics(2)
$d.Close($false)
try { $w.Quit() } catch {}
if (Test-Path -LiteralPath $Out) { 'pdf bytes: ' + (Get-Item -LiteralPath $Out).Length }

